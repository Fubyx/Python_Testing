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

def display_frame(): # not needed in production
    global frame
    while True:
        if frame is not None:
            cv2.imshow('Camera Stream', frame)
            if cv2.waitKey(1) == ord('q'):  # Exit on 'q' key press
                break

threading.Thread(target=display_frame, daemon=True).start()  # Start display thread

@app.route('/setpiurl')
def setPiUrl():
    global autopilot
    autopilot.pi_URL = "http://" + request.remote_addr + ":5000/controls"
    print(autopilot.pi_URL)
    return Response('success')

def autoControl(): #still partly pseudocode
    print("Autopilot started ---------------------------------------")
    global autopilot
    global frame
    global imProcessing
    global average_brightness

    if (frame is None):
        return

    #autopilot.setLightsState(0) 
    #imProcessing.setLightLevel(0)
    #autopilot.setDoorState(True)
    imProcessing.setModeToBall()
    imProcessing.setBallColor(autopilot.ballColor)
    imProcessing.setTargetColor(autopilot.doorColor)
    #prevLigths = autopilot.lights
    #helpCounter = 0
    #imProcessing.setTargetColor(autopilot.targetColor)
    #ballNotFoundCounter = 0

    ballx = None
    bally = None
    ball = []
    height, width, _ = frame.shape 
    #"""Incoming#----------------------------------
    TURN_AMOUNT = 50

    stage = 'ballFinding'
    dodgeObstacle = False
    dodgeDirection = None
    wallSide = None


    while not autopilot.stopped:
        time.sleep(0.5) # time to let the camera capture not blurry images 

        print(f"\n\ndistance front right: {autopilot.distanceFrontRight} \n" +
              f"distance front left: {autopilot.distanceFrontLeft} \n" +
              f"distance right: {autopilot.distanceRight} \n" +
              f"distance left: {autopilot.distanceLeft} \n" +
              f"distance back: {autopilot.distanceBack}" 
              )
        # Removed as this functionality is already added to recieve_frame
        #if (prevLigths != (average_brightness < 100)):
        #    prevLigths = (average_brightness < 100)
        #    imProcessing.setLightLevel(prevLigths)
        #    autopilot.lights = prevLigths

        # TODO: reacting to distance sencor data!
        if dodgeObstacle:
            if dodgeDirection == 'left' and autopilot.distanceFrontRight < 30:
                autopilot.turn(300, 100)
                print("Turn to the left to dodge front right obstacle")
            elif dodgeDirection == 'right' and autopilot.distanceFrontLeft < 30:
                autopilot.turn(300, -100)
                print("Turn to the right to dodge front left obstacle")
            else:
                dodgeObstacle = False
            continue
        if (autopilot.distanceFrontLeft < 20 or autopilot.distanceFrontRight < 20):
            dodgeObstacle = True
            if (autopilot.distanceFrontLeft < 20 and autopilot.distanceFrontRight < 20):
                if (wallSide == "left"):
                    dodgeDirection = "right"
                else:
                    dodgeDirection = "left"
                print("Obstacle straight ahead")
            elif (autopilot.distanceFrontLeft < autopilot.distanceFrontRight):
                dodgeDirection = 'right'
                wallSide = 'left'
                print("Obstacle front left")
            else:
                dodgeDirection = 'left'
                wallSide = 'right'
                print("Obstacle front right")
            continue
        
        match (stage):
            case 'ballFinding':
                #ball = imProcessing.getBallCoords(frame)
                ball = []
                if (len(ball) > 0):  
                    ballx = ball[0][0]/width
                    bally = ball[0][1]/height
                    print(f"ball found: x: {ballx}, y: {bally}")
                    autopilot.setDoorState(True)
                    stage = 'ballCatching'
                    continue
                if (wallSide == 'left' and autopilot.distanceLeft > 20):
                    autopilot.turn(300, 100)
                    print("turn left as no wall is detected on the left")
                elif (wallSide == 'right' and autopilot.distanceRight > 20):
                    autopilot.turn(300, -100)
                    print("turn right as no wall is detected on the right")
                autopilot.forward(300, 100)
                print("move forward")
            case 'ballCatching':
                return
                ball = imProcessing.getBallCoords(frame)
                if (len(ball) > 0):
                    ballx = ball[0][0]/width
                    bally = ball[0][1]/height
                    if ballx < 0.4:
                        autopilot.turn((0.5 - ballx) * TURN_AMOUNT, 100)
                    elif ballx > 0.6:
                        autopilot.turn((ballx-0.5) * TURN_AMOUNT, -100)
                    else:
                        if bally < 0.8:
                            autopilot.forward(40, 50)
                        elif (bally > 0.8):
                            #fine adjustment:
                            if ballx < 0.45:
                                autopilot.turn((0.5 - ballx) * TURN_AMOUNT, 100)
                            elif ballx > 0.55:
                                autopilot.turn((ballx-0.5) * TURN_AMOUNT, -100)
                            else:
                                autopilot.forward(40, 50)

                    
                    ballNotFoundCounter = 0 # here used to count the frames where imProcessing does not recognize a ball
                else:
                    if (ballNotFoundCounter > 5):
                        autopilot.forward(100, 100)
                        autopilot.setDoorState(False)
                        stage = 'goalFinding'
                    else:
                        ballNotFoundCounter+= 1
                
            case 'goalFinding':
                return
                imProcessing.setModeToTarget()
                # TODO: same as ballFinding
            case 'goalScoring':
                return
                # just copied from ballcatching!!!
                target = imProcessing.getTargetCoords(frame)
                if (len(target) > 0):
                    targetx = target[0][0]/width 
                    # An Fabian in dor Zukunft sobolt die getTarget funktion gmocht isch: isch targetx die mitte?
                    targety = target[0][1]/height
                    if targetx < 0.4:
                        autopilot.turn((0.5 - targetx) * TURN_AMOUNT, 100)
                    elif targetx > 0.6:
                        autopilot.turn((targetx-0.5) * TURN_AMOUNT, -100)
                    else:
                        if targety < 0.8:
                            autopilot.forward(100, 100)
                        elif (targety > 0.8):
                            #fine adjustment:
                            if targetx < 0.45:
                                autopilot.turn((0.5 - targetx) * TURN_AMOUNT, 100)
                            elif targetx > 0.55:
                                autopilot.turn((targetx-0.5) * TURN_AMOUNT, -100)
                            else:
                                autopilot.forward(100, 100)

                    time.sleep(0.5)
                    ballNotFoundCounter = 0 # here used to count the frames where imProcessing does not recognize a ball
                else:
                    if (ballNotFoundCounter > 10):
                        autopilot.doorState(True)
                        autopilot.forward(100, 100)
                        autopilot.forward(10, -100)
                        # now: PARTY!!!
                    else:
                        time.sleep(0.1)
                        ballNotFoundCounter+= 1
            case _:
                print("No clue what's happening anymore (stage matching error in autoControl() )")
    
    
    
        
        
    return
    #"""#---------------------------------

    #"""LOCAL (Fabian) ---------------------------------------------
    print(f"w: {width} h: {height}")
    someconstant = 600
    goalCenterx = None

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

    
    autopilot.setDoorState(True)
    
    while (not autopilot.stopped):
        ball = imProcessing.getBallCoords(frame)
        if (len(ball) > 0):
            ballx = ball[0][0]/width
            bally = ball[0][1]/height
            print(f"Ball found at x: {ballx} y: {bally}")
        else:
            print("Capturing ball")
            for i in range(0, 2):
                autopilot.forward(200, 100)
                time.sleep(0.3)
            autopilot.setDoorState(False)

            autopilot.setDoorState(False)

            
            #autopilot.forward(400, -100)
            #time.sleep(1)
            #ball = imProcessing.getBallCoords(frame)
            #if(len(ball) > 0):
            #    autopilot.setDoorState(True)
            #    continue
            break
        if ballx < 0.45:
            autopilot.turn((0.5 - ballx) * someconstant, 100)
            print("Turned to the left")
        elif ballx > 0.55:
            autopilot.turn((ballx-0.5) * someconstant, -100)
            print("Turned to the right")
        else:
            if(bally > 0.925):
                print("Capturing ball 2")
                for i in range(0, 2):
                    autopilot.forward(200, 100)
                    time.sleep(0.3)
                autopilot.setDoorState(False)

                #autopilot.forward(400, -100)
                #time.sleep(1)
                #ball = imProcessing.getBallCoords(frame)
                #if(len(ball) > 0):
                #    autopilot.setDoorState(True)
                #    continue
                break
            if(bally > 0.75):
                autopilot.forward(100, 100)
                print("Moved froward for 100ms")
            else:
                autopilot.forward(200, 100)
                print("Moved froward for 200ms")
                
        time.sleep(1)
        ballx = None
        bally = None
        
    return
    #"""
    #goalFound = False
    while (not autopilot.stopped):
        target = imProcessing.getTargetCoords(frame)
        if (target is not None):
            goalCenterx = (target[2] / 2 + target[0])/width
            goalLowerEdge = (target[1] + target[3])/height
            goalUpperEdge = target[1]/height
            print(f"Target found at x: {target[0]} y: {target[1]} centerX: {goalCenterx * width} %: {goalCenterx} lower: {goalLowerEdge} upper: {goalUpperEdge}")
            break
        else:
            #autopilot.turn(100, 100)
            pass
        time.sleep(1)
    
    time.sleep(1)
    inFrontOfGoal = False
    while not autopilot.stopped:
        target = imProcessing.getTargetCoords(frame)
        if (target is None):
            print("Lost the target")
            break

        goalCenterx = (target[2] / 2 + target[0])/width
        goalLowerEdge = (target[1] + target[3])/height
        goalUpperEdge = target[1]/height
        print(f"Target found at x: {target[0]} y: {target[1]} centerX: {goalCenterx * width} %: {goalCenterx} lower: {goalLowerEdge} upper: {goalUpperEdge}")
        if goalCenterx < 0.45:
            autopilot.turn((0.5 - goalCenterx) * someconstant, 100)
            print("Turned to the left")
        elif goalCenterx > 0.55:
            autopilot.turn((goalCenterx-0.5) * someconstant, -100)
            print("Turned to the right")
        else:
            if inFrontOfGoal:
                print("Shooting")
                autopilot.setDoorState(True)
                autopilot.forward(200, 100)
                time.sleep(1)
                autopilot.forward(200, 100)
                autopilot.setDoorState(False)
                break
            elif goalUpperEdge < 0.65:
                autopilot.forward(400, 75)
                
                print("moved forward for 400ms")
            #elif (goalUpperEdge > 0.1):
            #    autopilot.forward(200, 75)
            #    
            #    print("moved forward for 200ms")
            else:
                print("backing away for shooting")
                inFrontOfGoal = True
                autopilot.forward(200, -100)
            
        time.sleep(1)

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
    autopilot.settargetColor(data["doorColor"])
    try:
        if enableAutopilot:
            if autopilot.stopped:
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
            if(verticalSpeed > 0 or rotationalSpeed > 0):
                response = requests.post(autopilot.pi_URL, json={
                'verticalSpeed': verticalSpeed, 
                'rotationalSpeed' : rotationalSpeed, 
                'lightsState': autopilot.lights, 
                'doorState': autopilot.doorState,
                'duration': -1
                })
            else:
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