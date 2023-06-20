#!/usr/bin/python3
# -- coding: utf-8; mode: python --
"""
Flask server that will act as a callback for requests
from the Withings system.
"""


from flask import Flask, request, make_response, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root_route_handler():
    """
    This function is the authentication callback. 
    It will be responsible for saving the URL with the OAuth authentication code
    provided by Withings in a temporary file.
    """
    with open('url.tmp', 'w', encoding='UTF-8') as temp_file:
        temp_file.write(request.url)
    return render_template('index.html')

@app.route('/new_weights', methods=['GET', 'POST', 'HEAD'])
def notify_new_weight():
    """
    This function performs the Notify function of the application. 
    """
    print("New weight received!")
    return make_response(
        'OK',
        200
    )

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080
    )
