from flask import Flask, request, jsonify, Response, render_template
import cv2
import threading
import numpy as np
import requests
from autopilot import Autopilot
from imageProcessing import ImageProcessing

app = Flask(__name__)

frame = None  # Global variable to store the latest frame
image_data = None
PI_URL = "http://192.168.200.30:5000/controls"
ballColor = "blue"

imProcessing = ImageProcessing()

def display_frame(): # not needed in production
    global frame
    while True:
        if frame is not None:
            cv2.imshow('Camera Stream', frame)
            if cv2.waitKey(1) == ord('q'):  # Exit on 'q' key press
                break

threading.Thread(target=display_frame, daemon=True).start()  # Start display thread

autopilot = Autopilot(PI_URL=PI_URL)
def autoControl(): #still pseudocode
    global autopilot
    global imProcessing
    global frame
    global ballColor
    imProcessing.setModeToBall()
    imProcessing.setBallColor(ballColor)

    ballFound = False
    ballx = None
    bally = None
    someconstant = None
    while not autopilot.stop and not ballFound:
        ball = imProcessing.process(frame)
        if (len(ball) > 0):
            ballFound = True
            ballx = ball[0][0]
            bally = ball[0][1]
            noball = False
        else:
            autopilot.turn(100, 100)
    ballCaught = False
    while not autopilot.stop and not ballCaught:
        if ballx < 0.4:
            autopilot.turn((0.5 - ballx) * someconstant, 100)
        elif ballx > 0.6:
            autopilot.turn((ballx-0.5) * someconstant, 100)
        else:
            if bally > 0.5:
                autopilot.forward(100, 100)
            elif (bally > 0.8):
                autopilot.forward(50, 50)
            elif (noball):
                autopilot.forward(200, 50)
                autopilot.setDoorState(True)
                ballCaught = True
        ball = imProcessing.process(frame)
        if (len(ball) > 0):
            ballx = ball[0][0]
            bally = ball[0][1]
        else:
            noball = True

    """
    goalFound = False
    while not autopilot.stop and not ballFound:
        if (goalInImage):
            goalFound = True
        else:
            autopilot.turn(100, 100)
    inFrontOfGoal = False
    while not autopilot.stop and not inFrontOfGoal:
        if goalCenterx < 0.4:
            autopilot.turn((0.5 - goalCenterx) * someconstant, 80)
        elif goalCenterx > 0.6:
            autopilot.turn((goalCenterx-0.5) * someconstant, 80)
        else:
            if GoalLowerEdge > 0.3:
                autopilot.forward(100, 100)
            elif (GoalUpperEdge > 0.1):
                autopilot.forward(50, 50)
            else:
                autopilot.forward(200, 50)
                autopilot.setDoorState(False)
                inFrontOfGoal = True
    #"""


@app.route('/receive_frame', methods=['POST'])
def receive_frame():
    global frame
    global image_data
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image data'}), 400

    temp_data = request.files['image'].read()
    frame = cv2.cvtColor(cv2.imdecode(np.frombuffer(temp_data, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    frame = detect_objects(frame)
    image_data = cv2.imencode(".jpg", frame)[1].tobytes()

    return jsonify({'message': 'Frame received successfully'}), 200

@app.route('/img')
def img():
    global image_data
    return Response(image_data, mimetype='image/jpg')


@app.route('/controls', methods=['POST'])
def controls():
    global autopilot
    data = request.get_json(True)
    verticalSpeed = data["verticalSpeed"]
    rotationalSpeed = data["rotationalSpeed"]
    lightsState = data["lightsState"]
    doorState = data["doorState"]
    enableAutopilot = data["autopilot"]
    if enableAutopilot:
        autopilot.stop = False
        threading.Thread(target=autoControl, daemon=True).start()  # Start display thread
        return Response("success")
    
    autopilot.stop = True
    response = requests.post(PI_URL, json={'verticalSpeed': verticalSpeed, 'rotationalSpeed' : rotationalSpeed, 'lightsState': lightsState, 'doorState':doorState})
    try:
        response.raise_for_status()  # Raise exception on non-200 status codes
        print(f"sent successfully. Status code: {response.status_code}")
    except:
        print("sending failed")
    
    return Response("success")

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)