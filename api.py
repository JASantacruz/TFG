
from typing import Optional
from fhir import *
from pick import pick
import uuid
import json
import os
from dotenv import load_dotenv
import arrow
from withings_api.common import MeasureType
from requests.auth import HTTPBasicAuth
from utils.patient_utils import GetPatientFullUrl, GetPatientId, GetPatientName
from utils.observation_utils import GetObservationTotal, ParseResponse
# Desactivar los warnings de seguridad SSL
requests.packages.urllib3.disable_warnings() 

load_dotenv()
GET_METHOD = os.environ.get('GET_METHOD')
POST_METHOD = os.environ.get('POST_MEHOD')
PATIENT_ENDPOINT_URL = os.environ.get('PATIENT_ENDPOINT')
OBSERVATION_ENDPOINT_URL = os.environ.get('OBSERVATION_ENDPOINT')
USERNAME = os.environ.get('FHIR_USER')
PASSWORD = os.environ.get('PASSWORD')

def send_operations(method, full_url = PATIENT_ENDPOINT_URL, payload = None):
    try:
        if method == 'GET':
            return requests.get(url = full_url, auth=HTTPBasicAuth(USERNAME, PASSWORD), verify=False)
        elif method == 'POST':
            headers = {"Content-Type": "application/fhir+json"}
            return requests.post(url = full_url, headers = headers, auth = HTTPBasicAuth(USERNAME, PASSWORD), verify = False, data = payload)
    except Exception as e:
        print('There has been an error connecting to the FHIR server, please contact an administrator. Error: ', e)

def CreatePatient(api):
    """
    Create a new patient in the docker server.
    """
    user = api.get_credentials()
    name = input('Insert your name: ')
    surname = input('Insert your surname: ')
    birthdate = input('Insert your birthdate (YYYY-MM-DD): ')
    gender = pick(['Male', 'Female', 'Other'], 'Choose your gender',  indicator='>')[0] # [0] porque devuelve una tupla con el valor y el indice
    has_contact = pick(['Yes', 'No'], 'Do you have an emergency contact?', indicator='>')[0]
    contact_name = ''
    contact_relationship = ''
    contact_gender = ''
    
    if has_contact == 'Yes':
        contact_name = input('Insert your contact name: ')
        contact_relationship = input('Insert your contact relationship: ')
        contact_gender = pick(['Male', 'Female', 'Other'], 'Choose your contact gender', indicator='>')[0]
    
    msg=Patient(str(uuid.uuid4()), 'es', name, surname, gender.lower(), birthdate, True, contact_name, contact_relationship, contact_gender.lower())
    fhirmsg=PatientMsg(msg, user.access_token)

    return fhirmsg.fhirmsg

def GetPatientsWeight():
    """
    Get all patients weight from the docker.
    """
    try: 
        patientsNames = []
        patients = []
        for patient in GetPatients():
            jsonPatient = json.loads(patient)
            patientsNames.append(jsonPatient['name'])
            patients.append(jsonPatient)
        selected_patient = pick(patientsNames, 'Select a patient', indicator='>')[0]
        parsed_selected_patient = patients.pop(patientsNames.index(selected_patient))
        full_url = PATIENT_ENDPOINT_URL + '/' + parsed_selected_patient['id'] + '/Observation'
        response = send_operations(GET_METHOD, full_url)
        print(ParseResponse(response.json()))
        if GetObservationTotal(response) == 0:
            print('No weights available for the selected user')

    except Exception as e:
        print('Unexpected error: ', e)

def GetPatients():
    """Get all patients from the docker"""
    response = send_operations(GET_METHOD)
    response_entry = response.json()['entry']
    patients = []
    for i in response_entry:
        id = GetPatientId(i)
        name = GetPatientName(i)
        fullUrl = GetPatientFullUrl(i)
        patient = {
            'id': id,
            'name': name,
            'fullUrl': fullUrl
        }
        patients.append(json.dumps(patient))
    
    return patients

def AddMeasure(api):
    patientsNames = []
    patients = []
    for patient in GetPatients():
        jsonPatient = json.loads(patient)
        patientsNames.append(jsonPatient['name'])
        patients.append(jsonPatient)

    selected_patient = pick(patientsNames, 'Select a patient', indicator='>')[0]
    parsed_selected_patient = patients.pop(patientsNames.index(selected_patient))
    messages = []
    weights = []
    # Print values of the 365 days
    for i in api.measure_get_meas(MeasureType.WEIGHT, startdate=arrow.utcnow().shift(days=-365), enddate=arrow.utcnow(), lastupdate=None).measuregrps:
        for j in i.measures:
            weights.append('Date: ' + str(i.date.format(fmt='DD-MM-YYYY HH:mm')) + ' - Weight: ' + str(j.value / 1000 if len(str(j.value)) > 4 else j.value / 100) + ' kg')
            msgcoding=coding(code="8350-1", display="Body weight Measured --with clothes")
            user = api.get_credentials()
            excode=code(text="Weigth Array",codings=[msgcoding])
            effectiveDateTime=i.date.format('YYYY-MM-DD')
            valueQuantity=value("kg", j.value / 1000 if len(str(j.value)) > 4 else j.value / 100, "kg")
            msg=Observation(2,meta(),excode,encounter(parsed_selected_patient['fullUrl']),subject(parsed_selected_patient['fullUrl']), effectiveDateTime, valueQuantity)
            fhirmsg=ObservationMsg(msg, user.access_token)
            messages.append(fhirmsg.fhirmsg)
    
    index = pick(weights, 'Select a weight to add', indicator='>')[1]
    response = send_operations(method=POST_METHOD, full_url='{0}'.format(OBSERVATION_ENDPOINT_URL, parsed_selected_patient["id"]), payload=messages.pop(index))
    print(response)
