from RpiMotorLib import RpiMotorLib
import RPi.GPIO as GPIO 
import time

class Controls:
    # Static constants for pins and motortype
    MOTOR1EN_PIN = 23
    MOTOR1IN1PIN = 24
    MOTOR1IN2PIN = 25

    MOTOR2EN_PIN = 22
    MOTOR2IN1PIN = 17
    MOTOR2IN2PIN = 27

    DOOR_GPIO_PINS = [6, 13, 19, 26]
    MOTOR_TYPE = RpiMotorLib.BYJMotor("MyMotorOne", "28BYJ")

    LIGHT_PIN = None

    def __init__(self) -> None:
        # Variables used for doorhandling
        self.doorOpen = False
        self.doorTimer = 0
        self.leftSpeed = 0
        self.rightSpeed = 0
        self.lightsState = 2
        self.motor1PWM=GPIO.PWM(self.MOTOR1EN_PIN, 1000)
        self.motor2PWM=GPIO.PWM(self.MOTOR2EN_PIN, 1000)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.MOTOR1EN_PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR1IN1PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR1IN2PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR2EN_PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR2IN1PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR2EN_PIN, GPIO.OUT)

        GPIO.setup(self.LIGHT_PIN, GPIO.OUT)


        GPIO.output(self.MOTOR1IN1PIN, GPIO.LOW)
        GPIO.output(self.MOTOR1IN2PIN, GPIO.LOW)
        GPIO.output(self.MOTOR2IN1PIN, GPIO.LOW)
        GPIO.output(self.MOTOR2IN2PIN, GPIO.LOW)

        GPIO.output(self.LIGHT_PIN, GPIO.LOW)
    
    def changeValues(self, verticalSpeed, rotationalSpeed, lightsState, doorState):
        if(self.lightsState != lightsState):
            self.changeLighting(lightsState)
        if(self.doorOpen != doorState):
            self.moveDoor()
        

    def changeLighting(self, newState):
        if(newState == 0):
            pass


    def moveDoor(self):
        if time.time() - self.doorTimer > 1000:
            if self.doorOpen:
                self.doorTimer = time.time()
                self.MOTOR_TYPE.motor_run(self.DOOR_GPIO_PINS,0.005,128, False, False,"half", 0.01)
            else:
                self.doorTimer = time.time()
                self.MOTOR_TYPE.motor_run(self.DOOR_GPIO_PINS,0.005,128, True, False,"half", 0.01)

    def start(self):
        self.motor1PWM.start(0)
        self.motor2PWM.start(0)

    
        