import os
from glob import glob
from time import time
from SnConstants import *

# if True, prints debugging outputs
#DEBUG_STF = False
DEBUG_STF = True

class SnTempFrame:
    TempData = {
        'fTemp'         : None,
        'fTempTime'     : None,
        'goodTempCheck' : False
    }

    def GetTemperature(self):
        return SnTempFrame().TempData['fTemp']

    def GetTempTimeStamp(self):
        return SnTempFrame().TempData['fTempTime']

    def GetTempCheck(self):
        return SnTempFrame().TempData['goodTempCheck']

    def SetTempCheck(self, set):
        SnTempFrame().TempData['goodTempCheck'] = set

def checkFileExists(infn):
    if not os.path.exists(infn):
        return False
    else:
        return True

def ReadTempFile(TempFn):
    f = open(TempFn, 'r')
    lines = f.readlines()
    f.close()
    return lines

def TempReading():
    # Mount the Temp Probe Pin
    # Pin Infomation is Hard Coded in /boot/config.txt
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    TempFile = glob('/sys/bus/w1/devices/'+ '28*')[0] + '/w1_slave'

    if DEBUG_STF == True:
        print("Temperature File Location: %s" % TempFile)

    if checkFileExists(TempFile) == False:
        if DEBUG_STF == True:
            print("Temperature File Does Not Exists")
        return -1

    # Check if Temp File for Measurement
    lines = ReadTempFile(TempFile)
    if lines[0].strip()[-3:] == 'YES':
        temp = lines[1].find('t=')
        if temp != -1:

            # Read Temperature
            return float(lines[1][temp + 2:]) / 1000.0
        else:
            # Return -1 if Temp Data is Not Formatted Correctly
            return -1
    else:
        # Return -1 if Temp File has NO Measurement
        return -1

def UpdateTemperature():
    for tries in range(kMaxTempReadTries):
        if DEBUG_STF == True:
            print("Number of Tries Left: %d" % (3 - tries))
        Tdata = TempReading()

        if DEBUG_STF == True:
            print(Tdata)

        if Tdata != -1:
            SnTempFrame().TempData['fTemp'] = Tdata
            SnTempFrame().TempData['fTempTime'] = int(time() * 1000)
            SnTempFrame().SetTempCheck(True)

            if DEBUG_STF == True:
                print(SnTempFrame().GetTempCheck())
            break

        elif tries == 2:
            SnTempFrame().TempData['fTemp'] = Tdata
            SnTempFrame().TempData['fTempTime'] = int(time() * 1000)
            break

if __name__=="__main__":
    i = 0
    while i != 25:
        i += 1
        UpdateTemperature()

        if DEBUG_STF == True:
            print("Temperature Reading: " + str(SnTempFrame().TempData['fTemp']) + " C")
            print("Temperature Taken at: " + str(SnTempFrame().TempData['fTempTime']))