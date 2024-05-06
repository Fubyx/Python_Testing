from flask import Flask, render_template, Response, request
import cv2
import sys
import numpy
import RPi.GPIO as GPIO   
import time
import requests
from controls import Controls

from RpiMotorLib import RpiMotorLib

app = Flask(__name__)

control = Controls()

@app.route('/controls', methods=['POST'])
def controls():
    try:
        data = request.get_json(True)
        verticalSpeed = data["verticalSpeed"]
        rotationalSpeed = data["rotationalSpeed"]
        lightsState = data["lightsState"]
        doorState = data["doorState"]
        duration = data['duration']

        control.changeValues(verticalSpeed, rotationalSpeed, lightsState, doorState, duration)
    except Exception as e:
        print(e)
    return Response("success") # return things such as data from distance sensors


SERVER_URL = "http://192.168.86.113:5000/setpiurl"
response = requests.get(SERVER_URL)
try:
    response.raise_for_status()  # Raise exception on non-200 status codes
    #print(f"sent successfully. Status code: {response.status_code}")
except:
    print("sending failed")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True, threaded=True)
