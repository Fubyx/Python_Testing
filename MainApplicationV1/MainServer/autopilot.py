import time
import requests

class Autopilot:

    pi_URL = None
    stopped = True
    lights = 0 # 0 = Light (lights off); 1 = dark (lights on)
    doorState = False

    ballColor = "blue"

    distanceFrontLeft = 100
    distanceFrontRight = 100
    distanceLeft = 100
    distanceRight = 100
    distanceBack = 100
        
    
    def turn(self, milliseconds, power=100):
        response = requests.post(self.pi_URL, json={
            'verticalSpeed': 0, 
            'rotationalSpeed' : power, 
            'lightsState': self.lights, 
            'doorState':self.doorState
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
        response = requests.post(self.pi_URL, json={
            'verticalSpeed': power, 
            'rotationalSpeed' : 0, 
            'lightsState': self.lights, 
            'doorState':self.doorState
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
        response = requests.post(self.pi_URL, json={
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
        time.sleep(5)
    
    def setLightsState(self, newState):
        self.lights = newState
        self.stop()

    def setBallColor(self, newColor):
        self.ballColor = newColor
        