#https://stackoverflow.com/questions/62006135/streaming-video-from-a-python-server-to-a-web-client
from flask import Flask, render_template, Response, request
import cv2
import sys
import numpy
import RPi.GPIO as GPIO   

from RpiMotorLib import RpiMotorLib

GPIO.setwarnings(False)
#GPIO.cleanup()

motor1EnPin = 23
motor1In1Pin = 24
motor1In2Pin = 25

motor2In1Pin = 17
motor2In2Pin = 27
motor2EnPin = 22

doorGpioPins = [6, 13, 19, 26]
motorType = RpiMotorLib.BYJMotor("MyMotorOne", "28BYJ")

GPIO.setmode(GPIO.BCM)
GPIO.setup(motor1In1Pin, GPIO.OUT)
GPIO.setup(motor1In2Pin, GPIO.OUT)
GPIO.setup(motor1EnPin, GPIO.OUT)
GPIO.setup(motor2In1Pin, GPIO.OUT)
GPIO.setup(motor2In2Pin, GPIO.OUT)
GPIO.setup(motor2EnPin, GPIO.OUT)

GPIO.output(motor1In1Pin,GPIO.LOW)
GPIO.output(motor1In2Pin,GPIO.LOW)
GPIO.output(motor2In1Pin,GPIO.LOW)
GPIO.output(motor2In2Pin,GPIO.LOW)

motor1PWM=GPIO.PWM(motor1EnPin, 1000)
motor1PWM.start(0)
motor2PWM=GPIO.PWM(motor2EnPin, 1000)
motor2PWM.start(0)

app = Flask(__name__)

def get_frame():
    camera_port=0
    camera=cv2.VideoCapture(camera_port) #this makes a web cam object

    while True:
        retval, im = camera.read()
        imgencode=cv2.imencode('.jpg',im)[1]
        stringData=imgencode.tostring()
        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

    del(camera)

@app.route('/vid')
def vid():
     return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/controls', methods=['POST'])
def controls():
    data = request.get_json(True)
    verticalSpeed = data["verticalSpeed"]
    rotationalSpeed = data["rotationalSpeed"]
    #print(data)
    print("verticalSpeed: " + str(verticalSpeed))
    print("rotationalSpeed: " + str(rotationalSpeed))
    print("forceLights: " + str(data["forceLights"]))
    print("openDoor: " + str(data["openDoor"]))
    
    leftSpeed = (3 * verticalSpeed + rotationalSpeed) / 3
    rightSpeed = (3 *verticalSpeed - rotationalSpeed) / 3
    if leftSpeed > 100:
        leftSpeed = 100
    if leftSpeed < -100:
        leftSpeed = -100
    if rightSpeed > 100:
        rightSpeed = 100
    if rightSpeed < -100:
        rightSpeed = -100
        
    if leftSpeed > 0:
        GPIO.output(motor1In1Pin, GPIO.HIGH)
        GPIO.output(motor1In2Pin, GPIO.LOW)
    elif leftSpeed < 0:
        GPIO.output(motor1In1Pin, GPIO.LOW)
        GPIO.output(motor1In2Pin, GPIO.HIGH)
        leftSpeed = -leftSpeed
    else:
        GPIO.output(motor1In1Pin, GPIO.LOW)
        GPIO.output(motor1In2Pin, GPIO.LOW)

    if rightSpeed > 0:
        GPIO.output(motor2In1Pin, GPIO.HIGH)
        GPIO.output(motor2In2Pin, GPIO.LOW)
    elif rightSpeed < 0:
        GPIO.output(motor2In1Pin, GPIO.LOW)
        GPIO.output(motor2In2Pin, GPIO.HIGH)
        rightSpeed = -rightSpeed
    else:
        GPIO.output(motor2In1Pin, GPIO.LOW)
        GPIO.output(motor2In2Pin, GPIO.LOW)
        
    motor1PWM.ChangeDutyCycle(leftSpeed)
    motor2PWM.ChangeDutyCycle(rightSpeed)

    return Response("success")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True, threaded=True)



