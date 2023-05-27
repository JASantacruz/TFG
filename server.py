#!/usr/bin/python3
# -- coding: utf-8; mode: python --

from flask import Flask, request, make_response, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def rootRouteHandler():
    f = open('url.tmp', 'w')
    f.write(request.url)
    return render_template('index.html')


@app.route('/getweights', methods=['GET'])
def getWeightsRouteHandler():
    return make_response(
        'OK',
        200
    )

@app.route('/new_weights', methods=['GET', 'POST', 'HEAD'])
def notifyNewWeight():
    print('REQUEST -> ', request)
    print('REQUEST DATA -> ', request.data)
    print('REQUEST -> ', request.args)

    return make_response(
        'OK',
        200
    )

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080
    )
