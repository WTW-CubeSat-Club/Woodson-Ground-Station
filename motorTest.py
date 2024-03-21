from adafruit_motorkit import MotorKit 
from adafruit_motor import stepper

kit = MotorKit(i2c=board.I2C())

while True:
    kit.stepper1.onestep(style=stepper.MICROSTEP, direction=stepper.FORWARD)
    time.sleep(1)
    for i in range (0, 100):
        kit.stepper1.onestep(style=stepper.MICROSTEP, direction=stepper.FORWARD)
    time.sleep(1)
    for i in range (0, 10):
        kit.stepper1.step(10, style=stepper.MICROSTEP, direction=stepper.BACKWARD)
        
