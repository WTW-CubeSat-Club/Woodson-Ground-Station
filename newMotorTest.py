from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor
import time
import atexit

mh = Adafruit_MotorHAT()

def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)

stepper1 = mh.getStepper(200, 1)
stepper1.setSpeed(30)

while True:
    stepper1.step(10, Adafruit_MotorHat.FORWARD, Adafruit_MotorHAT.MICROSTEP)
    sleep(1)
    stepper1.step(100, Adafruit_MotorHat.BACKWARDm Adafruit_MotorHat.INTERLEAVE)    