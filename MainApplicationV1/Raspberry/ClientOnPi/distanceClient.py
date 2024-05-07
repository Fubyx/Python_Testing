import requests  # Import requests library
import RPi.GPIO as GPIO
import time
import threading

"""
from gpiozero import DistanceSensor
FRONT_LEFT = DistanceSensor(echo=8, trigger=9)
FRONT_RIGHT = DistanceSensor(echo=7, trigger=9)
LEFT = DistanceSensor(echo=12, trigger=9)
RIGHT = DistanceSensor(echo=21, trigger=9)
BACK = DistanceSensor(echo=5, trigger=9)

"""
GPIO.setmode(GPIO.BCM)

TRIG = 9
ECHO_FRONT_LEFT = 8
ECHO_FRONT_RIGHT = 7
ECHO_LEFT = 12
ECHO_RIGHT = 21
ECHO_BACK = 5

GPIO.setup(TRIG,GPIO.OUT)

GPIO.setup(ECHO_FRONT_LEFT,GPIO.IN)
GPIO.setup(ECHO_FRONT_RIGHT,GPIO.IN)
GPIO.setup(ECHO_LEFT,GPIO.IN)
GPIO.setup(ECHO_RIGHT,GPIO.IN)
GPIO.setup(ECHO_BACK,GPIO.IN)

GPIO.output(TRIG, False)


time.sleep(1)

# Server details (replace with your server's IP and port)
SERVER_IP = "192.168.86.113"
SERVER_PORT = 5000
SERVER_URL = "http://" + SERVER_IP + ':' + str(SERVER_PORT) + "/distanceData"


wait = True

def timer():
    global wait
    time.sleep(0.1)
    wait = False

def read(pin):
    global wait
    wait = True
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    t = threading.Thread(target=timer)
    t.start()

    while GPIO.input(pin)==0 and wait:
        pass
    pulse_start = time.time()
    while GPIO.input(pin)==1 and wait:
        pass
    pulse_end = time.time() 
    pulse_duration = pulse_end - pulse_start
    t.join()
    return round(pulse_duration * 17150, 2) # in cm

def capture_and_send_data():
    while True:
        try:

            distanceFrontLeft = read(ECHO_FRONT_LEFT)
            distanceFrontRight = read(ECHO_FRONT_RIGHT)
            distanceLeft = read(ECHO_LEFT)
            distanceRight = read(ECHO_RIGHT)
            distanceBack = read(ECHO_BACK)

            response = requests.post(SERVER_URL, json={'distanceFrontLeft' : distanceFrontLeft, 'distanceFrontRight' : distanceFrontRight, 'distanceLeft' : distanceLeft, 'distanceRight' : distanceRight, 'distanceBack' : distanceBack})

            #response = requests.post(SERVER_URL, json={'distanceFrontLeft' : FRONT_LEFT.distance, 'distanceFrontRight' : FRONT_RIGHT.distance, 'distanceLeft' : LEFT.distance, 'distanceRight' : RIGHT.distance, 'distanceBack' : BACK.distance})
            response.raise_for_status()  # Raise exception on non-200 status codes
            print("Frame sent successfully. Status code: " + str(response.status_code))
            time.sleep(0.5)
        except Exception as e:
            print("Error: "+ str(e))
            break

if __name__ == "__main__":
    capture_and_send_data()
