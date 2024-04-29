import time
import requests
from imageProcessing import ImageProcessing

class Autopilot:

    PI_URL = "http://192.168.200.30:5000/controls"
    imProcessing = ImageProcessing()
    stopped = False
    lights = False
    doorState = False

    ballColor = "blue"

    def __init__(self, PI_URL) -> None:
        self.PI_URL = PI_URL

    def findBall(self, frame):
        self.imProcessing.setModeToBall()
        self.imProcessing.setBallColor(self.ballColor)
        
        ballFound = False

        while not self.stopped and not ballFound:
            ball = self.imProcessing.getBallCoords(frame)
            print (ball)
            if (len(ball) > 0):
                height, width, channels = frame.shape 
                ballFound = True
                ballx = ball[0][0]/width
                bally = ball[0][1]/height
                print(f"x: {ballx}, y: {bally}")
                noball = False
            else:
                self.turn(100, 100)
            time.sleep(1)
            print('slept')
            
    def catchBall(self, frame):
        return
    
    def turn(self, milliseconds, power=100):
        self.stopped = False
        response = requests.post(self.PI_URL, json={
            'verticalSpeed': 0, 
            'rotationalSpeed' : power, 
            'lightsState': self.doorState, 
            'doorState':self.lights
            })
        try:
            response.raise_for_status()  # Raise exception on non-200 status codes
            #print(f"sent successfully. Status code: {response.status_code}")
        except:
            print("sending failed")
        for i in range(1, 10):
            time.sleep(0.0001*milliseconds)
            if self.stopped:
                return
        self.stop()


    def forward(self, milliseconds, power=100):
        self.stopped = False
        response = requests.post(self.PI_URL, json={
            'verticalSpeed': power, 
            'rotationalSpeed' : 0, 
            'lightsState': self.doorState, 
            'doorState':self.lights
            })
        try:
            response.raise_for_status()  # Raise exception on non-200 status codes
            #print(f"sent successfully. Status code: {response.status_code}")
        except:
            print("sending failed")
        for i in range(1, 10):
            time.sleep(0.01*milliseconds)
            if self.stopped:
                return
        self.stop()

    def stop(self):
        response = requests.post(self.PI_URL, json={
            'verticalSpeed': 0, 
            'rotationalSpeed' : 0, 
            'lightsState': self.lights, 
            'doorState':self.doorState
            })
        try:
            response.raise_for_status()  # Raise exception on non-200 status codes
            #print(f"sent successfully. Status code: {response.status_code}")
            #self.stopped = True
        except:
            print("sending failed")
    
    def setDoorState(self, newState):
        self.doorState = newState
        self.stop()
    
    def setLightsState(self, newState):
        self.lights = newState
        self.stop()

    def setBallColor(self, newColor):
        self.ballColor = newColor
        