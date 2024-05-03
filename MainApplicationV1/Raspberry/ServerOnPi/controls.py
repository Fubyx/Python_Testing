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

    LIGHT_PIN = 16

    def __init__(self) -> None:
        # Variables used for doorhandling
        self.doorOpen = False
        self.doorTimer = 0  

        self.leftSpeed = 0
        self.rightSpeed = 0
        self.lightsState = 0 # 0 = off, 1 = on

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.MOTOR1EN_PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR1IN1PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR1IN2PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR2EN_PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR2IN1PIN, GPIO.OUT)
        GPIO.setup(self.MOTOR2IN2PIN, GPIO.OUT)

        GPIO.setup(self.LIGHT_PIN, GPIO.OUT)

        self.motor1PWM=GPIO.PWM(self.MOTOR1EN_PIN, 1000)
        self.motor2PWM=GPIO.PWM(self.MOTOR2EN_PIN, 1000)

        GPIO.output(self.MOTOR1IN1PIN, GPIO.LOW)
        GPIO.output(self.MOTOR1IN2PIN, GPIO.LOW)
        GPIO.output(self.MOTOR2IN1PIN, GPIO.LOW)
        GPIO.output(self.MOTOR2IN2PIN, GPIO.LOW)

        GPIO.output(self.LIGHT_PIN, GPIO.LOW)
        self.start()
    
    def changeValues(self, verticalSpeed, rotationalSpeed, lightsState, doorState):
        if(self.lightsState != lightsState):
            self.changeLighting(lightsState)

        if(self.doorOpen != doorState):
            self.moveDoor()
        leftSpeed = verticalSpeed - rotationalSpeed
        rightSpeed = verticalSpeed + rotationalSpeed
        if leftSpeed > 100:
            leftSpeed = 100
        if leftSpeed < -100:
            leftSpeed = -100
        if rightSpeed > 100:
            rightSpeed = 100
        if rightSpeed < -100:
            rightSpeed = -100
            
        outLeft1 = GPIO.HIGH if leftSpeed > 0 else GPIO.LOW
        outLeft2 = GPIO.HIGH if leftSpeed < 0 else GPIO.LOW
        GPIO.output(self.MOTOR1IN1PIN, outLeft1)
        GPIO.output(self.MOTOR1IN2PIN, outLeft2)
        
        outRight1 = GPIO.HIGH if rightSpeed > 0 else GPIO.LOW
        outRight2 = GPIO.HIGH if rightSpeed < 0 else GPIO.LOW
        GPIO.output(self.MOTOR2IN1PIN, outRight1)
        GPIO.output(self.MOTOR2IN2PIN, outRight2)

        self.motor1PWM.ChangeDutyCycle(abs(leftSpeed))
        self.motor2PWM.ChangeDutyCycle(abs(rightSpeed))

    def changeLighting(self, newState):
        self.lightsState = newState
        if newState == 0:
            GPIO.output(self.LIGHT_PIN, GPIO.LOW)
        elif newState == 1:
            GPIO.output(self.LIGHT_PIN, GPIO.HIGH)


    def moveDoor(self):
        if time.time() - self.doorTimer > 5:
            self.doorTimer = time.time()
            self.doorOpen = not self.doorOpen
            if self.doorOpen:
                self.MOTOR_TYPE.motor_run(self.DOOR_GPIO_PINS,0.002,128, True, False,"half", 0.01)
            else:
                self.MOTOR_TYPE.motor_run(self.DOOR_GPIO_PINS,0.002,128, False, False,"half", 0.01)

    def start(self):
        self.motor1PWM.start(0)
        self.motor2PWM.start(0)

    
        
