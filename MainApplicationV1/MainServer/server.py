from flask import Flask, request, jsonify, Response, render_template
import cv2
import threading
import numpy as np
import requests

app = Flask(__name__)

frame = None  # Global variable to store the latest frame
image_data = None

# Funktion zur Konturerkennung und Markierung mit Rechtecken
def detect_objects(frame, min_area=500):
    # Konvertiere das Bild in Graustufen
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Wende den Kantendetektor an
    edges = cv2.Canny(gray, 50, 150)

    cv2.imshow("Canny", edges)
    
    # Finde Konturen im Bild
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Durchlaufe alle gefundenen Konturen
    for contour in contours:
        # Berechne das umgebende Rechteck um die Kontur
        x, y, w, h = cv2.boundingRect(contour)
        
        # Überprüfe, ob das Rechteck die Mindestgröße hat
        if w * h < min_area:
            continue
        
        # Überprüfe, ob das Rechteck von einem anderen Rechteck umgeben ist
        surrounded = False
        for other_contour in contours:
            if other_contour is not contour:
                other_x, other_y, other_w, other_h = cv2.boundingRect(other_contour)
                if x > other_x and y > other_y and x + w < other_x + other_w and y + h < other_y + other_h:
                    surrounded = True
                    break
        
        if surrounded:
            continue
        
        # Zeichne ein Rechteck um die Kontur
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return frame

def display_frame():
    global frame
    while True:
        if frame is not None:
            cv2.imshow('Camera Stream', frame)
            if cv2.waitKey(1) == ord('q'):  # Exit on 'q' key press
                break

threading.Thread(target=display_frame, daemon=True).start()  # Start display thread

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
    data = request.get_json(True)
    verticalSpeed = data["verticalSpeed"]
    rotationalSpeed = data["rotationalSpeed"]
    lightsState = data["lightsState"]
    doorState = data["doorState"]
    autopilot = data["autopilot"]

    PI_URL = "http://192.168.200.30:5000/controls"
    response = requests.post(PI_URL, json={'verticalSpeed': verticalSpeed, 'rotationalSpeed' : rotationalSpeed, 'lightsState': lightsState, 'doorState':doorState})
    try:
        response.raise_for_status()  # Raise exception on non-200 status codes
        print(f"sent successfully. Status code: {response.status_code}")
    except:
        print("sending failed")
    
    return Response("success") # return things such as data from distance sensors

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)