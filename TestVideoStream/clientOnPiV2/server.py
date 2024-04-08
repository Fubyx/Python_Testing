from flask import Flask, request, jsonify, Response
import cv2
import threading
import numpy as np

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
    frame = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)  # Update global frame

    return jsonify({'message': 'Frame received successfully'}), 200

@app.route('/img')
def img():
    return Response(b'--frame\r\n'
                    b'Content-Type: text/plain\r\n\r\n'+
                    image_data+b'\r\n',
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)