import os
import time
import datetime
import pandas as pd
import motorControl
from rtlsdr import RtlSdr
import threading

mode = (os.path.isfile('/Documents/RunWithConnection.txt'))


def sdrstart(freq, timeEnd):
    sdr = RtlSdr()

    sdr.sample_rate = 2.048e6 #Hz
    sdr.center_freq = freq
    sdr.freq_correction = 60 #PPM
    sdr.gain = 'auto'

    currentTime = datetime.datetime()

    filename = (currentTime.strftime("%Y:%m:%d_%H:%M_%S") + ".txt")
    location = os.path.join('/Documents/dataFolder', 'filename')

    with open(location, 'w') as file:
        while True:
            samples = sdr.read_samples(256*1024)
            bytes_data = bytearray(samples)
            text = bytes_data.decode('ascii', errors='ignore')
            file.write(text)
            if (time.time() > timeEnd):
                break

    

class target:
    def __init__(self, name, norad_id, trackStart, trackEnd, startLat, startLong, endLat, endLong, alt, priority, dLfreq):
        self.name = name
        self.norad_id = norad_id
        self.trackStart = trackStart
        self.trackEnd = trackEnd
        self.startLat = startLat
        self.startLong = startLong
        self.endLat = endLat
        self.endLong = endLong
        self.alt = alt
        self.priority = priority
        self.dLfreq = dLfreq

while True:
    if (mode):
        print("Run with connection ")
    else:
        if ((os.path.isfile('/Targets.csv'))):
            targList = pd.read_csv('Targets.csv')
            df = pd.DataFrame(targList)
            timeNow = time.time()
            row = df.loc[df['trackStart']>(timeNow+5)].iloc[0] ##Find first available target (time start is more than 5 seconds from now)
            nowTarget = target(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]) ##Adds values to target object
            higherPriorityRow = df.loc[df['priority']>nowTarget.priority].iloc[0] ##Finds next target with higher priority
            higherPriority = target(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]) ##Adds values to target object
            if (higherPriority.trackStart < nowTarget.trackEnd):
                nowTarget = higherPriority
            ##Add better priority code
            motorControl.moveTo(nowTarget.startAz, nowTarget.startEl)
            time.sleep(nowTarget.startTrack - time.time())
            t1 = threading(target=(motorControl.pointTrack()), args=(nowTarget.startLat, nowTarget.startLong, nowTarget.endLat, nowTarget.endLong, nowTarget.alt, nowTarget.trackStart, nowTarget.trackEnd))
            t2 = threading(target=sdrstart(), args=(nowTarget.dLfreq, nowTarget.trackEnd))
            t1.start() ##Multithreads the track and the radio functions
            t2.start()
            t1.join()##Pause current thread until t1 is done
            t2.join()##Pause current thread until t2 is done
            
