from flask import Flask, request, jsonify, Response
import cv2
import threading
import numpy as np
import requests

app = Flask(__name__)
frame = None  # Global variable to store the latest frame
image_data = None

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

    if 'image' not in request.files:
        return jsonify({'error': 'Missing image data'}), 400

    image_data = request.files['image'].read()
    frame = cv2.cvtColor(cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    
    return jsonify({'message': 'Frame received successfully'}), 200

@app.route('/img')
def img():
    return Response(b'--frame\r\n'+
                    b'Content-Type: text/plain\r\n\r\n'+
                    image_data+b'\r\n',
                    mimetype='multipart/x-mixed-replace; boundary=frame')


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)