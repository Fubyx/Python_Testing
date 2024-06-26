#!/usr/bin/env python3
""" 
Test example file for file: RpiMotorLib.py class BYJMotor

Comment in code  blocks marked:
"EMERGENCY STOP BUTTON CODE" to Test motor stop method with Push Button
and place push button to VCC on GPIO 17 :: VCC - PB1Pin1 , GPIO17 - PB1Pin2
"""

import time 
import RPi.GPIO as GPIO

"""
# For development USE local library testing import
# 1. Comment in Next 3 lines 
# 2. Comment out in "Production installed library import"
# 3. change RpiMotorLib.BYJMotor to BYJMotor below
import sys
sys.path.insert(0, '/home/gavin/Documents/tech/RpiMotorLib/RpiMotorLib')
from RpiMotorLib import BYJMotor
"""

# Production installed library import 
from RpiMotorLib import RpiMotorLib

"""
# EMERGENCY STOP BUTTON CODE: See docstring
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
"""

# Declare an named instance of class pass your custom name and type of motor
mymotortest = RpiMotorLib.BYJMotor("MyMotorOne", "28BYJ")

def main():
    """main function loop"""
    
    # ====== tests for motor 28BYJ48 ====
    
    """
    # EMERGENCY STOP BUTTON CODE:  See docstring
    GPIO.add_event_detect(17, GPIO.RISING, callback=button_callback)
    """
    
    # Connect GPIO to [IN1 , IN2 , IN3 ,IN4] on Motor PCB
    GpioPins = [6, 13, 19, 26]
    
    # Arguments  for motor run function
    # (GPIOPins, stepdelay, steps, counterclockwise, verbose, steptype, initdelay)
    
    time.sleep(0.1)
    input("Press <Enter> to continue Test1")
    mymotortest.motor_run(GpioPins,0.001,128, True, False,"full", 0.01)
    time.sleep(1)
    input("Press <Enter> to continue  Test2")
    mymotortest.motor_run(GpioPins,.001,256, False, True,"half", .05)
    time.sleep(1)
    input("Press <Enter> to continue  Test3")
    mymotortest.motor_run(GpioPins,.01, 5, False, True,"half", 2)
    time.sleep(1) 
    input("Press <Enter> to continue  Test4")
    mymotortest.motor_run(GpioPins,.05, 50, True, True,"wave", .05)
    time.sleep(1)
    input("Press <Enter> to continue  Test5")
    mymotortest.motor_run(GpioPins,.01,512,False,False,"half", .05)


"""
# EMERGENCY STOP BUTTON CODE: See docstring
def button_callback(channel):
    print("Test file: Stopping motor")
    mymotortest.motor_stop()
"""

# ===================MAIN===============================

if __name__ == '__main__':
   
    print("START")
    main()
    GPIO.cleanup() # Optional 
    exit()
    
    
# =====================END===============================