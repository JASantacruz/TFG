import json

def GetObservationTotal(observation):
    total = observation.json()['total']
    return total

def GetObservationDisplay(observation):
    display = observation['resource']['code']['coding'][0]['display']
    return display or ''

def GetObservationValue(observation):
    value = observation['resource']['valueQuantity']['value']
    return value or ''

def GetObservationUnit(observation):
    unit = observation['resource']['valueQuantity']['unit']
    return unit or ''

def ParseResponse(response):
    observations = ''
    for i in response['entry']:
        observations += 'Observation - '+ str(GetObservationDisplay(i)) + ' ' + str(GetObservationValue(i)) + str(GetObservationUnit(i)) + '\n'

    return observations 