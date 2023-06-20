"""
This file contains the logic for creating resources in FHIR format.
"""
# pylint: disable=invalid-name
import json
from datetime import datetime

class value:
    """
    Value of a Observation
    """
    def __init__(self, unit, value, code, system="http://unitsofmeasure.org"):
        self.unit=unit
        self.value=value
        self.code=code
        self.system=system

class encounter:
    """
    Encounter of a Observation
    """
    def __init__(self,routineID):
        self.reference=routineID

class subject:
    """
    Subject of a Observation
    """
    def __init__(self,userID):
        self.reference=userID

class coding:
    """
    Coding of a Code
    """
    def __init__(self,system="http://loinc.org",code="",display=""):
        self.system=system
        self.code=code
        self.display=display


class code:
    """
    Code of a Observation
    """
    def __init__(self, text="Business description of the exercise", codings=[]):
        self.text=text
        self.coding=codings

class meta:
    def __init__(self, versionId=2, lastUpdated=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")):
        self.versionId=str(versionId)
        self.lastUpdated=lastUpdated

class formatDate:
    def __init__(self, date, format):
        self.date=date.format(format)


class derivedFrom:
    def __init__(self, reference, display):
        self.reference=reference
        self.display=display 

class Observation:
    """
    Create a new Observation
    """
    def __init__(self,id, metadata, code, encounter, subject, effectiveDateTime, valueQuantity):
        self.resourceType="Observation"
        self.id=str(id)
        self.status="final"
        self.meta=metadata
        self.code=code
        self.encounter=encounter
        self.subject=subject
        self.effectiveDateTime=effectiveDateTime
        self.valueQuantity=valueQuantity


class ObservationEncoder(json.JSONEncoder):
    """
    Class to encode Observation to JSON
    """
    def default(self, o):
        return o.__dict__


class ObservationMsg:
    """
    Create a new Observation Message in FHIR Format
    """
    def __init__(self, observation:Observation, token):
        self.observation=observation
        self.token=token
        self.fhirmsg=json.dumps(self.observation, indent=4,cls=ObservationEncoder,default=lambda o: o.__dict__)

class Patient:
    """
    Create a new Patient
    """
    def __init__(self, patient_id, language, given_name, family_name, gender, birth_date, active, contact_name, contact_relationship, contact_gender):
        self.resourceType="Patient"
        self.language=language
        self.identifier=[{"value":patient_id}]
        self.name=[{"given":[given_name], "family":family_name}]
        self.gender=gender
        self.birthDate=birth_date
        self.active=active
        # If contact_name is not empty, then add contact information
        if contact_name != '':
            self.contact=[{
                "relationship": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                        "code": "C",
                        "display": "Emergency Contact"
                    }],
                    "text": contact_relationship
                }],
                "name": { "given": [contact_name]},
                "gender": contact_gender,
            }]

class PatientEncoder(json.JSONEncoder):
    """
    Class to encode Patient to JSON
    """
    def default(self, o):
        return o.__dict__


class PatientMsg:
    """
    Create a new Patient Message in FHIR Format
    """
    def __init__(self, patient:Patient, token):
        self.patient=patient
        self.token=token
        self.fhirmsg=json.dumps(self.patient, indent=4,cls=PatientEncoder,default=lambda o: o.__dict__)