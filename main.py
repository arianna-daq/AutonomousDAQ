# python main.py

import numpy as np
import smbus
import RPi.GPIO as GPIO
from SnConstants import *
from SnPreCompOptions import *
from SnConfigFrame import *

def SetSstDACs(bus):
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

                dv = SnConfigFrame().GetDAC(ch, dc)

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
                    #bus.write_i2c_block_data(dadr, dn, [int(MSB), int(LSB)])
                    dok = True
                except OSError:
                    dok = False

            if DEBUG == True:
                print("Channel %d: Transmitted? %s " % (ch, dok))



if __name__=="__main__":
    if DEBUG == True:
        print("System Starting...")

    # Initialize and Assign IO pins
    bus = smbus.SMBus(1)

    GPIO.setmode(GPIO.BOARD)

    # Output Pins
    GPIO.setup(33, GPIO.OUT, initial=0)     # Card/ Data Taking Power [False]
    GPIO.setup(36, GPIO.OUT, initial=0)     # Amp Power [False]
    GPIO.setup(38, GPIO.OUT, initial=0)     # Unused Pin [False]
    GPIO.setup(40, GPIO.OUT, initial=0)     # Iridium Power [False]

    #GPIO.setup(35, GPIO.OUT, initial=0)  # Power Probe 1
    #GPIO.setup(37, GPIO.OUT, initial=0)  # Power Probe 2

    # Pins 39, 34 are GND Pins

    LoadDEFCONF()
    if DEBUG == True:
        print("Configuration File Loaded.")

    #SetSstDACs(0)

