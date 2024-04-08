from flask import Flask, render_template, Response, request
import cv2
import sys
import numpy
import RPi.GPIO as GPIO   
import time
from controls import Controls

from RpiMotorLib import RpiMotorLib

app = Flask(__name__)

control = Controls()

@app.route('/controls', methods=['POST'])
def controls():
    data = request.get_json(True)
    verticalSpeed = data["verticalSpeed"]
    rotationalSpeed = data["rotationalSpeed"]
    lightsState = data["lightsState"]
    doorState = data["doorState"]

    control.changeValues(verticalSpeed, rotationalSpeed, lightsState, doorState)
    
    return Response("success") # return things such as data from distance sensors


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True, threaded=True)