from api import CreatePatient, GetPatientsWeight, AddMeasure
from pick import pick

def ShowOptions(api):
    """
    Muestra las opciones disponibles para el usuario.
    En función de la opción seleccionada, se ejecutará una función u otra.
    """ 
    title = 'Select an option'
    options = ['Create a patient', 'Get patients weight', 'Add a measure to a patient']

    option, index = pick(options, title, indicator='>')

                    
    if option == 'Create a patient':
        CreatePatient(api)

    elif option == 'Get patients weight':
        GetPatientsWeight()

    elif option == 'Add a measure to a patient':
        AddMeasure(api)
