# python main.py

import numpy as np
from smbus import SMBus
import RPi.GPIO as GPIO
import time

from SnConstants import *
from SnPreCompOptions import *
from SnConfigFrame import *
from SnTempFrame import *

# Create Shortcuts
C = SnConfigFrame()
T = SnTempFrame()

# Initialize and Assign IO pins
bus = SMBus(1)                          # I2C Pins 3, 5
GPIO.setmode(GPIO.BOARD)                # Sets GPIO Function Input Format [Pin or GPIO]

# Output Pins
GPIO.setup(33, GPIO.OUT, initial=0)     # Card/ Data Taking Power [False]
GPIO.setup(36, GPIO.OUT, initial=0)     # Amp Power [False]
GPIO.setup(38, GPIO.OUT, initial=0)     # UNUSED Pin [False]
GPIO.setup(40, GPIO.OUT, initial=0)     # Iridium Power [False]

# Input Pins
GPIO.setup(35, GPIO.IN)    # Power Probe 1 [UNUSED Pin]
GPIO.setup(37, GPIO.IN)    # Power Probe 2 [UNUSED Pin]

# Pin 32 Temp Probe [No IO Initialization Needed]
# GND Pins 34, 39

def SetSstDACs():
    """Sends the High and Low Thresholds to the LTC2657 DAC Chip via I2C"""

    # Init Variables
    dadr, dv, dn = 0, 0, 0
    LSB, MSB = 0, 0

    if DEBUG == True:
        print("Sending DAC thresholds...")

    for ch in range(kNchans):
        dadr = kLTC2657Addr[int(ch / kChansPerLTC2657)]

        for dc in range(kNchanDacs):
            dok = False

            for tries in range(kMaxDacSetTries):
                if dok == True:
                    break

                if DEBUG == True:
                    print("Start I2C for dc= %d, ch=%d, try=%d, dok=%s" % (dc, ch, tries, dok))
                    print("Address %s (%s)" % (hex(dadr), format(dadr, '08b')))

                # Address for Each DAC Register
                dn = (kChansPerLTC2657*kNchanDacs) - (dc*kChansPerLTC2657) - kChansPerLTC2657 + (ch % kChansPerLTC2657)

                # Raise Error for Invalid Code for LTC2657 DAC Chip
                if dn > 7:
                    print("TotDacs=%d, dc=%d, ch=%d, ChansPerLTC2657=%d, dn=%d" % (kTotDacs, dc, ch, kChansPerLTC2657, dn))
                    raise("chan/dac combination too big for 3 bits!")

                # Build Data Bitstream to Send to LTC2657 DAC Chip
                dn |= (kUpdateDacCmd << 4)

                if DEBUG == True:
                    print("Write Command and Register Address %s (%s)" % (hex(dn), format(dn, '08b')))
                    print("%d Bits per DAC Register" % (DAC_BITS))

                dv = C.GetDAC(ch, dc)

                if DEBUG == True:
                    print("Channel %d High(1)/Low(0)=%d Threshold dv=%d (%s)" % (ch, dc, dv, format(dv, '08b')))

                MSB = (dv & 65280) >> 8
                LSB = (dv & 255)

                if DEBUG == True:
                    print("MSB:%s" % format(MSB, '08b'))
                    print("LSB:%s" % format(LSB, '08b'))

                # Try Send Data Bitstream to DAC Chip via I2C
                # If Error is Raised then Try Again
                try:
                    bus.write_i2c_block_data(dadr, dn, [int(MSB), int(LSB)])
                    dok = True
                except OSError:
                    dok = False

            if DEBUG == True:
                print("Channel %d: Transmitted? %s " % (ch, dok))

def ProcTempCheck():
    # Reset Temp Check Monitor
    T.goodTempCheck = False
    UpdateTemperature()

    if T.goodTempCheck == True:
        #Save Temp to .dat file
        if DEBUG == True:
            print("Temp %d [C] Saved to SD at %d [ms]" % T.GetTemperature(), T.GetTempTimeStamp())
    else:
        # Save -1 in temp as sign of issue
        if DEBUG == True:
            print("Error while taking Temp: Value -1 at %d [ms]" % T.GetTempTimeStamp())


if __name__=="__main__":
    if DEBUG == True:
        print("Main Code Starting...")

    # Load & Set Board Configurations
    LoadDEFCONF()
    if DEBUG == True:
        print("Configuration File Loaded.")

    # Set Pins to Configuration Settings [DATA TAKING PHASE]
    GPIO.output(33, C.GetPowerOnFor(kCardDatTak))   # Card/ Data Taking Power
    GPIO.output(36, C.GetPowerOnFor(kAmpsDatTak))   # Amp Power
    GPIO.output(40, C.GetPowerOnFor(kIridDatTak))   # Iridium Power

    ProcTempCheck()

    ##SetSstDACs()

    time.sleep(10)
    GPIO.cleanup()

