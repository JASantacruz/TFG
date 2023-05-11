def GetPatientId(patient):
    """Returns the id of the patient"""
    patient_id = patient['resource']['id']
    return patient_id

def GetPatientName(patient):
    """Parse the name of the patient"""
    name = patient['resource']['name']
    return str(name[0]['given'][0] + ' ' + name[0]['family'])

def GetPatientFullUrl(patient):
    """Parse the fullurl of the patient"""
    fullurl = patient['fullUrl']
    return fullurl