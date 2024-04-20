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
    someconstant = 0.1
    while not autopilot.stop and not ballFound:
        ball = imProcessing.getBallCoords(frame)
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

def mark_ball_in_color(frame, lower_color, upper_color,min_radius, color_tolerance):
    # Konvertiere das Bild von BGR zu HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Erzeuge einen Maskenbereich für die angegebene Farbe
    mask = cv2.inRange(hsv, lower_color, upper_color)

    cv2.imshow("Farbe", mask)

    """
    #Apply Gradient
    ksize = 3
    gX = cv2.Sobel(mask, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=ksize)
    gY = cv2.Sobel(mask, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=ksize)
    gX = cv2.convertScaleAbs(gX)
    gY = cv2.convertScaleAbs(gY)
    combined = cv2.addWeighted(gX, 0.5, gY, 0.5, 0)
    cv2.imshow("Combined", combined)
    
    

    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 50, param1=90, param2=30, minRadius=10, maxRadius=300)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles: 
            if r > 10:
                cv2.circle(frame, (x, y), r, (0, 0, 255), 2)
    """
    edges = cv2.Canny(mask, 50, 150, apertureSize=3)
    cv2.imshow("Canny", edges)

    # Finde Konturen im Maskenbereich
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    

    for contour in contours:
            # Berechne das Zentrum und den Radius des Balls
            (x, y), radius = cv2.minEnclosingCircle(contour)
            radius = int(radius)


            #59.041175842285156 und r= 6
            #65.85074615478516 und r= 8
            #87.98148345947266 und r= 13
            #138.0 und r= 23
            #371.89569091796875 und r= 79
            #426.7767333984375 und r= 91
            
            # Überprüfe, ob der Radius größer als der Mindestradius ist
            if radius > min_radius:
                print(str(y) + " und r= " + str(radius))
                # Erzeuge eine Maske für den Kreisbereich
                mask_circle = np.zeros_like(frame[:, :, 0], dtype="uint8")
                cv2.circle(mask_circle, (int(x), int(y)), radius, (255, 255, 255), -1)

                # Wende die Maske an, um die Farbinformationen innerhalb des Kreises zu extrahieren
                masked_frame = cv2.bitwise_and(frame, frame, mask=mask_circle)

                # Überprüfe die Farbkonsistenz anhand der Standardabweichung
                color_variance = np.std(masked_frame[mask_circle == 255], axis=0)
                if np.all(color_variance < color_tolerance):
                    # Zeichne den Kreis, wenn die Farbe konsistent ist
                    cv2.circle(frame, (int(x), int(y)), radius, (0, 255, 0), 2)

    return frame

@app.route('/receive_frame', methods=['POST'])
def receive_frame():
    global frame
    global image_data
    if 'image' not in request.files:
        return jsonify({'error': 'Missing image data'}), 400

    temp_data = request.files['image'].read()
    frame = cv2.cvtColor(cv2.imdecode(np.frombuffer(temp_data, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    
    
    
    min_radius = 5
    color_tolerance = 50        #darf nicht kleiner als 35 sein
    #blau
    lower_color = np.array([190/2, 30*255/100, 0*255/100])
    upper_color = np.array([240/2, 100*255/100, 100*255/100])
    frame = mark_ball_in_color(frame, lower_color, upper_color, min_radius, color_tolerance)
    


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