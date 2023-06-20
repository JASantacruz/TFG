"""
This file contains the modularised logic of the function
of displaying options to the user.
"""
# pylint: disable=invalid-name
from pick import pick
from api import CreatePatient, GetPatientsWeight, AddMeasure

def ShowOptions(api):
    """
    Displays the options available to the user.
    Depending on the option selected, one function or another will be executed.
    """

    title = 'Select an option'
    options = ['Create a patient', 'Get patients weight', 'Add a measure to a patient']

    option = pick(options, title, indicator='>')[0]

    if option == 'Create a patient':
        CreatePatient(api)

    elif option == 'Get patients weight':
        GetPatientsWeight()

    elif option == 'Add a measure to a patient':
        AddMeasure(api)
