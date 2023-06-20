"""
This file contains the logic of the functions useful for observations.
"""
# pylint: disable=invalid-name

def GetObservationTotal(observation):
    """
    This function returns the total count of observations for a patient.
    """
    total = observation.json()['total']
    return total

def GetObservationDisplay(observation):
    """
    This function returns the display of the observation.
    """
    display = observation['resource']['code']['coding'][0]['display']
    return display or ''

def GetObservationValue(observation):
    """
    This function returns the value of the observation.
    """
    value = observation['resource']['valueQuantity']['value']
    return value or ''

def GetObservationUnit(observation):
    """
    This function returns the unit of the observation.
    """
    unit = observation['resource']['valueQuantity']['unit']
    return unit or ''

def ParseResponse(response):
    """
    This function parses the response of the request.
    """
    observations = ''
    for i in response['entry']:
        observations += 'Observation - ' + str(GetObservationDisplay(i)) + ' ' + str(GetObservationValue(i)) + str(GetObservationUnit(i)) + '\n'

    return observations
