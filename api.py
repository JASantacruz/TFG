"""
This file contains the logic to connect to the FHIR server
and send the requests with the different options offered by the application.
"""
# pylint: disable=invalid-name
import uuid
import json
import os
import requests
import arrow
from dotenv import load_dotenv
from pick import pick
from withings_api.common import MeasureType
from requests import exceptions
from requests.auth import HTTPBasicAuth
from requests.packages import urllib3
from fhir import *
from utils.patient_utils import GetPatientFullUrl, GetPatientId, GetPatientName
from utils.observation_utils import GetObservationTotal, ParseResponse

# Disable SSL security warnings
urllib3.disable_warnings()

load_dotenv()
GET_METHOD = os.environ.get('GET_METHOD')
POST_METHOD = os.environ.get('POST_MEHOD')
PUT_METHOD = os.environ.get('PUT_METHOD')
DELETE_METHOD = os.environ.get('DELETE_METHOD')
PATIENT_ENDPOINT_URL = os.environ.get('PATIENT_ENDPOINT')
OBSERVATION_ENDPOINT_URL = os.environ.get('OBSERVATION_ENDPOINT')
USERNAME = os.environ.get('FHIR_USER')
PASSWORD = os.environ.get('PASSWORD')

def send_operations(method, full_url = PATIENT_ENDPOINT_URL, payload = None):
    """
    Function in charge of sending operations to the FHIR server.
    """
    try:
        if method == GET_METHOD:
            return requests.get(
                url = full_url,
                auth=HTTPBasicAuth(USERNAME, PASSWORD),
                verify=False,
                timeout=20
                )
        elif method == POST_METHOD:
            headers = {"Content-Type": "application/fhir+json"}
            return requests.post(
                url = full_url,
                headers = headers,
                auth = HTTPBasicAuth(USERNAME, PASSWORD),
                verify = False,
                data = payload,
                timeout=20
                )
        elif method == PUT_METHOD:
            headers = {"Content-Type": "application/fhir+json"}
            return requests.put(
                url = full_url,
                headers = headers,
                auth = HTTPBasicAuth(USERNAME, PASSWORD),
                verify = False,
                data = payload,
                timeout=20
            )

        elif method == DELETE_METHOD:
            return requests.delete(
                url = full_url,
                auth = HTTPBasicAuth(USERNAME, PASSWORD),
                verify = False,
                timeout=20
                )

    except exceptions.ConnectionError as connection_error:
        print('There has been an error connecting to the FHIR server,'
              +'The server is not operative. Error: ', connection_error)
    except exceptions.Timeout as timeout_error:
        print('There has been an error connecting to the FHIR server,'
              +'Timeout. Error: ', timeout_error)
    except exceptions.RequestException as request_error:
        print('There has been an error connecting to the FHIR server,'
              +' please contact an administrator. Error: ', request_error)

def CreatePatient(api):
    """
    Create a new patient in the docker server.
    """
    user = api.get_credentials()
    name = input('Insert your name: ')
    surname = input('Insert your surname: ')
    birthdate = input('Insert your birthdate (YYYY-MM-DD): ')
    gender = pick(['Male', 'Female', 'Other'], 'Choose your gender',  indicator='>')[0]
    has_contact = pick(['Yes', 'No'], 'Do you have an emergency contact?', indicator='>')[0]
    contact_name = ''
    contact_relationship = ''
    contact_gender = ''

    if has_contact == 'Yes':
        contact_name = input('Insert your contact name: ')
        contact_relationship = input('Insert your contact relationship: ')
        contact_gender = pick(['Male', 'Female', 'Other'],
            'Choose your contact gender', indicator='>')[0]

    msg=Patient(
        str(uuid.uuid4()),
        'es',
        name,
        surname,
        gender.lower(),
        birthdate,
        True,
        contact_name,
        contact_relationship,
        contact_gender.lower()
    )
    fhirmsg=PatientMsg(msg, user.access_token)

    return fhirmsg.fhirmsg

def GetPatientsWeight():
    """
    Get all patients weight from the docker.
    """
    try:
        patients_names = []
        patients = []
        for patient in GetPatients():
            json_patient = json.loads(patient)
            patients_names.append(json_patient['name'])
            patients.append(json_patient)
        selected_patient = pick(patients_names, 'Select a patient', indicator='>')[0]
        parsed_selected_patient = patients.pop(patients_names.index(selected_patient))
        full_url = PATIENT_ENDPOINT_URL + '/' + parsed_selected_patient['id'] + '/Observation'
        response = send_operations(GET_METHOD, full_url)

        print(ParseResponse(response.json()))

        if GetObservationTotal(response) == 0:
            print('No weights available for the selected user')

    except Exception as exception:
        print('Unexpected error: ', exception)

def GetPatients():
    """Get all patients from the docker"""
    response = send_operations(GET_METHOD)
    response_entry = response.json()['entry']
    patients = []
    for i in response_entry:
        id = GetPatientId(i)
        name = GetPatientName(i)
        full_url = GetPatientFullUrl(i)
        patient = {
            'id': id,
            'name': name,
            'fullUrl': full_url
        }
        patients.append(json.dumps(patient))

    return patients

def AddMeasure(api):
    """
    Function in charge of the logic of adding a measure to a patient
    """
    patients_names = []
    patients = []
    for patient in GetPatients():
        json_patient = json.loads(patient)
        patients_names.append(json_patient['name'])
        patients.append(json_patient)

    selected_patient = pick(patients_names, 'Select a patient', indicator='>')[0]
    parsed_selected_patient = patients.pop(patients_names.index(selected_patient))
    messages = []
    weights = []
    # Print values of the 365 days
    for i in api.measure_get_meas(MeasureType.WEIGHT,
                                  startdate=arrow.utcnow().shift(days=-365),
                                  enddate=arrow.utcnow(),
                                  lastupdate=None).measuregrps:
        for j in i.measures:
            weights.append('Date: '
                + str(i.date.format(fmt='DD-MM-YYYY HH:mm'))
                + ' - Weight: '
                + str(j.value / 1000 if len(str(j.value)) > 4 else j.value / 100)
                + ' kg')

            msgcoding=coding(code="8350-1", display="Body weight Measured --with clothes")
            user = api.get_credentials()
            excode=code(text="Weigth Array",codings=[msgcoding])
            effective_date_time=i.date.format('YYYY-MM-DD')
            value_quantity=value(
                unit ="kg",
                value = j.value / 1000 if len(str(j.value)) > 4 else j.value / 100,
                code = "kg")
            msg=Observation(
                id = 2,
                metadata = meta(),
                code = excode,
                encounter = encounter(parsed_selected_patient['fullUrl']),
                subject = subject(parsed_selected_patient['fullUrl']),
                effectiveDateTime = effective_date_time,
                valueQuantity = value_quantity)
            fhirmsg=ObservationMsg(msg, user.access_token)
            messages.append(fhirmsg.fhirmsg)

    index = pick(weights, 'Select a weight to add', indicator='>')[1]
    response = send_operations(
        method=POST_METHOD,
        full_url='{0}'.format(OBSERVATION_ENDPOINT_URL),
        payload=messages.pop(index))
    print(response)
