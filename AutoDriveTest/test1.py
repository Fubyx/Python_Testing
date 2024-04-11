import requests
import time

PI_URL = "http://192.168.200.30:5000/controls"
def turn():
    response = requests.post(PI_URL, json={
        'verticalSpeed': 0, 
        'rotationalSpeed' : 50, 
        'lightsState': False, 
        'doorState':False
        })
    try:
        response.raise_for_status()  # Raise exception on non-200 status codes
        print(f"sent successfully. Status code: {response.status_code}")
    except:
        print("sending failed")

def stop():
    response = requests.post(PI_URL, json={
        'verticalSpeed': 0, 
        'rotationalSpeed' : 0, 
        'lightsState': False, 
        'doorState':False
        })
    try:
        response.raise_for_status()  # Raise exception on non-200 status codes
        print(f"sent successfully. Status code: {response.status_code}")
    except:
        print("sending failed")

turn()
time.sleep(5)
stop()