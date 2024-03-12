import time 
from adafruit_motorkit import MotorKit 
from adafruit_motor import stepper
import digitalio
import board
import pyproj
import math

kit = MotorKit(i2c=board.I2C())

#stepper1 : M1/M2 Port : Azimuth
#stepper2 : M3/M4 Port : Elevation

const_stepsPerDegree = 1 #Number of motor steps to move 1 degree 
const_degreesPerStep = 1/const_stepsPerDegree

const_gsLat = 38.840425 #DD Coordinates
const_gsLong = -77.275516
const_gsAlt = 127 #127 Meters above sea level
const_earthRadius = 6378000 #Earth radius meters

az_hall_pin = digitalio.DigitalInOut(board.D2)
az_hall_pin.direction = digitalio.Direction.INPUT
el_hall_pin = digitalio.DigitalInOut(board.D3)
el_hall_pin.direction = digitalio.Direction.INPUT
power_pin = digitalio.DigitalInOut(board.D4)
power_pin.direction = digitalio.Direction.OUTPUT
power_pin.Pull.DOWN

azPos = 0.00 #0 for North, 270 West, etc.
elPos = 0.00 #0 for forwards level, 90 forwards vertical, 180 max

def checkVals():
    if (azPos < 0.00 or azPos >= 360.00):
        azPos = 0.00
    if (elPos < 0.00):
        elPos = 0.00
    elif (elPos > 180.00):
        elPos = 180.00

def home():
    power_pin.Pull.UP
    if az_hall_pin == True:
        hallAz = True
    else:
        hallAz = False
    if el_hall_pin == True:
        hallEl = True
    else:
        hallEl = False
    while (hallAz != 1):
        kit.stepper1.onestep(style=stepper.MICROSTEP, direction=stepper.FORWARD)
    azPos = 0.00

    while (hallEl != 1):
        kit.stepper2.onestep(style=stepper.MICROSTEP, direction=stepper.BACKWARD)
    elPos = 0.00

    power_pin.Pull.DOWN

def moveTo(az, el):
    azTarg = az
    elTarg = el

    elDif = abs(elTarg - elPos) * const_stepsPerDegree
    azDif = abs(azTarg) * const_stepsPerDegree

    #Determines which direction is faster
    rotateDir = 1
    if (azTarg < azPos):
        if ((azPos - azTarg) < 180.00):
            rotateDir = 1 #Rotate Backwards
        else: 
            rotateDir = 0 #Rotate Forwards
    elif (azPos < azTarg):
        if ((azTarg - azPos) < 180.00):
            rotateDir = 0 #Rotate Backwards

    while((elDif != 0) or (azDif != 0)):
        
        #Rotate to azimuth
        if (azPos != azTarg):
            if (rotateDir == 1):
                kit.stepper1.onestep(style=stepper.MICROSTEP, direction=stepper.FORWARD)
                azPos += const_degreesPerStep
            else:
                kit.stepper1.onestep(style=stepper.MICROSTEP, direction=stepper.BACKWARD)
                azPos -= const_degreesPerStep


        #Rotate to elevation
        if (elPos > elTarg and elPos > 0.00):
                kit.stepper2.onestep(style=stepper.MICROSTEP, direction=stepper.BACKWARD)
                elPos -= const_degreesPerStep
        elif (elPos < elTarg and elPos < 180.00):
                kit.stepper2.onestep(style=stepper.MICROSTEP, direction=stepper.FORWARD)
                elPos += const_degreesPerStep
        checkVals()
        elDif = abs(elTarg - elPos) * const_stepsPerDegree
        azDif = abs(azTarg) * const_stepsPerDegree


def pointToCoords(lat, long, alt):
    gsLatRad = abs(90 - const_gsLat).toRadians()
    latRad = abs(90-lat).toRadians()
    gsLongRad = abs(const_gsLong).toRadians()
    longRad = abs(long).toRadians()

    geodesic = pyproj.Geod(ellps='WGS84')
    fwd_azimuth,back_azimuth,distance = geodesic.inv(const_gsLong, const_gsLat, long, lat) #Find azimuth/bearing using geodesic calculation
    centralAngle = math.acos((const_earthRadius**2)*math.sin(latRad)*math.sin(gsLatRad)*math.cos(longRad-gsLongRad)+math.cos(latRad)*math.cos(gsLatRad)) #Spherical Law of Cosines to determine central angle
    angleElevation = math.asin(alt*(math.sin(centralAngle)/math.sqrt((const_gsAlt)**2+alt^2-2*alt*(const_gsAlt)*math.cos(centralAngle)))) - 90 #Finds angle of elevation between GS and sat

    fwd_azimuth = fwd_azimuth.toDegrees()
    angleElevation = angleElevation.toDegrees()

    moveTo(fwd_azimuth, angleElevation)

def pointTrack(latStart, longStart, latEnd, longEnd, alt, timeStart, timeEnd):
    geodesic = pyproj.Geod(ellps='WGS84')
    initialAz, initialEl, distance = geodesic.inv(const_gsLong, const_gsLat, longStart, latStart)
    endAz, endEl, distance = geodesic.inv(const_gsLong, const_gsLat, longEnd, latEnd)
    pointToCoords(latStart, longStart, alt)
    degreesAzPerSecond = (initialAz - endAz)/(timeEnd - timeStart)
    degreesElPerSecond = (initialEl - endEl)/(timeEnd - timeStart)
    if (time.time() > (timeStart-100) and time.time() < (timeStart + 100)):
        while (time.time() < timeEnd):
            moveTo(azPos + degreesAzPerSecond, elPos + degreesElPerSecond)
    