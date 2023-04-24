from SnConstants import *
import RPi.GPIO as GPIO

# if True, prints debugging outputs
DEBUG_SEF = False
#DEBUG_SEF = True

ReadOutSelect   = 31

class SnEventFrame:
    fData     = np.empty(kTotSamps)
    fStop     = np.empty(kNstopBytes)
    fMbedTime = None
    fEvtNum   = None
    fDTms     = None
    fTrgNum   = None
    fTrgBits  = None
    fCRC      = None

def ClearEvent(clearTrigs, clearWaveData):
    SnEventFrame().fMbedTime = 0

    if clearWaveData:
        SnEventFrame().fData = np.empty(kTotSamps)
        SnEventFrame().fStop = np.empty(kNstopBytes)
        snEventFrame().fCRC  = 0

    if clearTrigs:
        SnEventFrame().fEvtNum  = 0
        SnEventFrame().fTrgNum  = 0
        SnEventFrame().fTrgBits = 0

def ReadWaveformsSST(spi, ReadingOut):
    global ReadOutSelect

    GPIO.output(ReadOutSelect, True)

    spi.open(0,0)
    Bytes = spi.readbytes(3)
    spi.close()

    return Bytes

def BytesToHex(Bytes):
    return ''.join(["0x%02X " % x for x in Bytes]).strip()