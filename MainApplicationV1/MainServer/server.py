from flask import Flask, request, jsonify, Response, render_template
import cv2
import threading
import numpy as np
import requests
from autopilot import Autopilot
import time
from imageProcessing import ImageProcessing

app = Flask(__name__)

# Remove success messages of get/post etc
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

frame = None  # Global variable to store the latest frame
image_data = None
PI_URL = "http://192.168.86.30:5000/controls"

average_brightness = 100
ballColor = "blue"
imProcessing = ImageProcessing()


autopilot = Autopilot(PI_URL=PI_URL)
def autoControl(): #still pseudocode
    global autopilot
    global frame
    global imProcessing
    global ballColor

    autopilot.setLightsState(1)
    autopilot.setBallColor(ballColor)
    imProcessing.setModeToBall()
    imProcessing.setBallColor(ballColor)
        
    ballx = None
    bally = None
    height = 480
    width = 640

    ballFound = False
    while (not autopilot.stopped) and (not ballFound):
        ball = imProcessing.getBallCoords(frame)
        print (ball)
        if (len(ball) > 0):
            height, width, channels = frame.shape 
            ballFound = True
            ballx = ball[0][0]/width
            bally = ball[0][1]/height
            print(f"x: {ballx}, y: {bally}")
            noball = False
        else:
            autopilot.turn(100, 100)
        time.sleep(1)
        print('slept')

    
    
    someconstant = 0.1
    
    ballCaught = False
    return
    while not autopilot.stopped and not ballCaught:
        ball = autopilot.imProcessing.getBallCoords(frame)
        if (len(ball) > 0):
            ballx = ball[0][0]/width
            bally = ball[0][1]/height
        else:
            noball = True
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
                autopilot.setDoorState(True)
                autopilot.forward(200, 50)
                autopilot.setDoorState(False)
                ballCaught = True
        

    """
    goalFound = False
    while not autopilot.stopped and not ballFound:
        if (goalInImage):
            goalFound = True
        else:
            autopilot.turn(100, 100)
    inFrontOfGoal = False
    while not autopilot.stopped and not inFrontOfGoal:
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
    global imProcessing
    global average_brightness
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image data'}), 400

    temp_data = request.files['image'].read()
    frame = cv2.cvtColor(cv2.imdecode(np.frombuffer(temp_data, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    
    #frame = detect_objects(frame)
    image_data = cv2.imencode(".jpg", frame)[1].tobytes()

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Calculate the mean of the grayscale image
    average_brightness = np.mean(gray_image)
    print(average_brightness)
    #for testing on PC
    #"""
    imProcessing.setModeToBall()
    imProcessing.setBallColor("blue")
    imProcessing.getBallCoords(frame)
    #"""

    return jsonify({'message': 'Frame received successfully'}), 200

@app.route('/img')
def img():
    global image_data
    return Response(image_data, mimetype='image/jpg')

@app.route('/distanceData', methods=['POST'])
def distanceData():
    global autopilot
    data = request.get_json(True)
    autopilot.distanceFrontLeft = data["distanceFrontLeft"]
    autopilot.distanceFrontRight= data["distanceFrontRight"]
    autopilot.distanceLeft      = data["distanceLeft"]
    autopilot.distanceRight     = data["distanceRight"]
    autopilot.distanceBack      = data["distanceBack"]
    print(
        'autopilot.distanceFrontLeft '+autopilot.distanceFrontLeft +'\n'
        'autopilot.distanceFrontRight'+autopilot.distanceFrontRight+'\n'
        'autopilot.distanceLeft      '+autopilot.distanceLeft      +'\n'
        'autopilot.distanceRight     '+autopilot.distanceRight     +'\n'
        'autopilot.distanceBack      '+autopilot.distanceBack      +'\n'
    )
    return Response("success")

@app.route('/controls', methods=['POST'])
def controls():
    global autopilot
    global ballColor
    data = request.get_json(True)
    verticalSpeed = data["verticalSpeed"]
    rotationalSpeed = data["rotationalSpeed"]
    lightsState = data["lightsState"]
    doorState = data["doorState"]
    enableAutopilot = data["autopilot"]
    ballColor = data["ballColor"]
    try:
        
        if enableAutopilot:
            autopilot.stopped = False
            threading.Thread(target=autoControl, daemon=False).start()
            return Response("success")
        
        autopilot.stopped = True
        response = requests.post(PI_URL, json={'verticalSpeed': verticalSpeed, 'rotationalSpeed' : rotationalSpeed, 'lightsState': lightsState, 'doorState':doorState})
        try:
            response.raise_for_status()  # Raise exception on non-200 status codes
            #print(f"sent successfully. Status code: {response.status_code}")
        except:
            print("sending failed")
        
        return Response("success")
    except Exception as e:
        print(e)
        return Response("Error")

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)