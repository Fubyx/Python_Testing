import time
import requests

class Autopilot:

    PI_URL = "http://192.168.200.30:5000/controls"
    stop = False
    lights = False
    doorState = False

    def __init__(self, PI_URL) -> None:
        self.PI_URL = PI_URL
    
    def turn(self, milliseconds, power=100):
        response = requests.post(self.PI_URL, json={
            'verticalSpeed': 0, 
            'rotationalSpeed' : power, 
            'lightsState': self.doorState, 
            'doorState':self.lights
            })
        try:
            response.raise_for_status()  # Raise exception on non-200 status codes
            print(f"sent successfully. Status code: {response.status_code}")
        except:
            print("sending failed")
        for i in range(1, 10):
            time.sleep(0.01*milliseconds)
            if self.stop:
                return
        self.stop()

    def forward(self, milliseconds, power=100):
        response = requests.post(self.PI_URL, json={
            'verticalSpeed': power, 
            'rotationalSpeed' : 0, 
            'lightsState': self.doorState, 
            'doorState':self.lights
            })
        try:
            response.raise_for_status()  # Raise exception on non-200 status codes
            print(f"sent successfully. Status code: {response.status_code}")
        except:
            print("sending failed")
        for i in range(1, 10):
            time.sleep(0.01*milliseconds)
            if self.stop:
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
            print(f"sent successfully. Status code: {response.status_code}")
        except:
            print("sending failed")
    def setDoorState(self, newState):
        self.doorState = newState
        self.stop()
    
    def setLightsState(self, newState):
        self.lights = newState
        self.stop()