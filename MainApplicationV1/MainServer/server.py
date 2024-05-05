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

#fabians hotspot pi_URL: "http://192.168.86.30:5000/controls" 

average_brightness = 100
imProcessing = ImageProcessing()

autopilot = Autopilot()

@app.route('/setpiurl')
def setPiUrl():
    global autopilot
    autopilot.pi_URL = "http://" + request.remote_addr + ":5000/controls"
    print(autopilot.pi_URL)
    return Response('success')

def autoControl(): #still pseudocode
    global autopilot
    global frame
    global imProcessing

    if (frame is None):
        return

    #autopilot.setLightsState(0) 
    #imProcessing.setLightLevel(0)
    imProcessing.setModeToBall()
    imProcessing.setBallColor(autopilot.ballColor)
        
    ballx = None
    bally = None
    ball = []
    height = 480
    width = 640

    #"""
    # searching ball:
    ballFound = False
    while (not autopilot.stopped) and (not ballFound):
        ball = imProcessing.getBallCoords(frame)
        if (len(ball) > 0):  
            ballx = ball[0][0]/width
            bally = ball[0][1]/height
            print(f"x: {ballx}, y: {bally}")
            break
        else:
            autopilot.turn(400, 100)
        time.sleep(1) # to let the camera capture not blurry images

    
    someconstant = 400
    autopilot.setDoorState(True)
    
    while (not autopilot.stopped):
        ball = imProcessing.getBallCoords(frame)
        if (len(ball) > 0):
            ballx = ball[0][0]/width
            bally = ball[0][1]/height
        else:
            autopilot.forward(200, 60)
            autopilot.setDoorState(False)
            break
        if ballx < 0.44:
            autopilot.turn((0.5 - ballx) * someconstant, 100)
        elif ballx > 0.55:
            autopilot.turn((ballx-0.5) * someconstant, -100)
        else:
            if bally < 0.8:
                autopilot.forward(400, 75)
            elif (bally > 0.8):
                autopilot.forward(400, 75)
                
        time.sleep(1)
        ballx = None
        bally = None
        
    return
    #"""
    goalFound = False
    while (not autopilot.stopped) and (not ballFound):
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
    average_brightness = round(average_brightness, 2)
    if (not autopilot.stopped): # When Autopilot is enabled automatically switch light state
        if(average_brightness < 50 and autopilot.lights == 0):
            autopilot.setLightsState(1)
            imProcessing.setLightLevel(1)
        elif(average_brightness > 50 and autopilot.lights == 1):
            autopilot.setLightsState(0)
            imProcessing.setLightLevel(0)

    #for testing on PC
    """
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
    #print(f"autopilot.distanceFrontLeft  {autopilot.distanceFrontLeft} \n" +
    #       f" autopilot.distanceFrontRight  {autopilot.distanceFrontRight}\n" + 
    #       f" autopilot.distanceLeft  {autopilot.distanceLeft}\n" + 
    #       f" autopilot.distanceRight  {autopilot.distanceRight}\n" + 
    #       f" autopilot.distanceBack  {autopilot.distanceBack}\n" + 
    #      "")
    
    return Response("success")

@app.route('/pidata', methods=['GET'])
def getPiData():
    global autopilot
    global average_brightness
    return Response(
        '{' +
        '"distanceFrontLeft" :'+str(autopilot.distanceFrontLeft )+',\n'
        '"distanceFrontRight":'+str(autopilot.distanceFrontRight)+',\n'
        '"distanceLeft"      :'+str(autopilot.distanceLeft      )+',\n'
        '"distanceRight"     :'+str(autopilot.distanceRight     )+',\n'
        '"distanceBack"      :'+str(autopilot.distanceBack      )+',\n'
        '"brightness"        :'+str(average_brightness          )+'}'
    )

@app.route('/controls', methods=['POST'])
def controls():
    global autopilot
    data = request.get_json(True)
    enableAutopilot = data["autopilot"]
    autopilot.setBallColor(data["ballColor"])
    try:
        if enableAutopilot:
            autopilot.stopped = False
            threading.Thread(target=autoControl, daemon=False).start()
            return Response("success")
        
        verticalSpeed = data["verticalSpeed"]
        rotationalSpeed = data["rotationalSpeed"]
        autopilot.lights = data["lightsState"]
        autopilot.doorState = data["doorState"]
        if not autopilot.stopped:
            autopilot.stop()
            autopilot.stopped = True
        if (autopilot.pi_URL is not None):
            response = requests.post(autopilot.pi_URL, json={
                'verticalSpeed': verticalSpeed, 
                'rotationalSpeed' : rotationalSpeed, 
                'lightsState': autopilot.lights, 
                'doorState': autopilot.doorState,
                'duration': -1
                })
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
    app.run(host='0.0.0.0', port=5000)