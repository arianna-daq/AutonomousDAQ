# python main.py

import numpy as np
from smbus import SMBus
import RPi.GPIO as GPIO
import time

from SnConstants import *
from SnPreCompOptions import *
from SnTempFrame import SnTempFrame, UpdateTemperature
from SnConfigFrame import SnConfigFrame, LoadDEFCONF
from SnTempFrame import *

# Create Shortcuts
M = MainFrame()
C = SnConfigFrame()

# Initialize and Assign IO pins
bus = SMBus(1)  # I2C Pins 3, 5
GPIO.setmode(GPIO.BOARD)  # Sets GPIO Function Input Format [Pin or GPIO]

# Output Pins

GPIO.setup(8, GPIO.OUT, initial=False)   # Reset Chips
GPIO.setup(12, GPIO.OUT, initial=False)  # Enable Thermal Triggers
GPIO.setup(13, GPIO.OUT, initial=False)  # Execute Forced Trigger
GPIO.setup(15, GPIO.OUT, initial=True)   # FPGA Differential Select
GPIO.setup(16, GPIO.OUT, initial=False)   # Dual Threshold Select !!!!!!!!!!!!!!!!!!!!!!!!!!
GPIO.setup(26, GPIO.OUT, initial=False)  # Majority Logic Low Bit
GPIO.setup(29, GPIO.OUT, initial=False)  # Majority Logic High Bit
GPIO.setup(31, GPIO.OUT, initial=False)  # Reading Out Data Select
GPIO.setup(33, GPIO.OUT, initial=False)  # Card/ Data Taking Power
GPIO.setup(36, GPIO.OUT, initial=False)  # Amp Power
GPIO.setup(40, GPIO.OUT, initial=False)  # Iridium Power

# Input Pins
GPIO.setup(7, GPIO.IN)  # Data Ready Flag

# USED PINS
# GPIO.setup(35, GPIO.IN)    # Power Probe 1 [UNUSED Pin]
# GPIO.setup(37, GPIO.IN)    # Power Probe 2 [UNUSED Pin]
# GPIO.setup(38, GPIO.OUT)   # UNUSED Pin

# Pin 32 Temp Probe [No IO Initialization Needed]
# See README for More Details Regarding P32.
# GND Pins 6, 9, 14, 20, 25, 30,34, 39

# Initialize Flag Variables
gFirstEvt    = True     # First Event of Sequence
gReadingOut  = False    # Readout Data from FPGA
gOpenCommWin = False    # Open Comm Window
gCheckTemp   = False    # Check Temperature

def AreCardsPowered():  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    return True

def SetSstDACs(bus):
    """Sends the High and Low Thresholds to the LTC2657 DAC Chip via I2C"""

    # Init Variables
    dadr, dv, dn = 0, 0, 0
    LSB, MSB = 0, 0

    if DEBUG:
        print("Sending DAC thresholds...")

    for ch in range(kNchans):
        dadr = kLTC2657Addr[int(ch / kChansPerLTC2657)]

        for dc in range(kNchanDacs):
            dok = False

            for tries in range(kMaxDacSetTries):
                if dok == True:
                    break

                if DEBUG:
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

                if DEBUG:
                    print("Write Command and Register Address %s (%s)" % (hex(dn), format(dn, '08b')))
                    print("%d Bits per DAC Register" % (DAC_BITS))

                dv = SnConfigFrame().GetDAC(ch, dc)

                if DEBUG:
                    print("Channel %d High(1)/Low(0)=%d Threshold dv=%d (%s)" % (ch, dc, dv, format(dv, '08b')))

                MSB = (dv & 65280) >> 8
                LSB = (dv & 255)

                if DEBUG:
                    print("MSB:%s" % format(MSB, '08b'))
                    print("LSB:%s" % format(LSB, '08b'))

                # Try Send Data Bitstream to DAC Chip via I2C
                # If Error is Raised then Try Again
                try:
                    bus.write_i2c_block_data(dadr, dn, [int(MSB), int(LSB)])
                    dok = True
                except OSError:
                    dok = False

            if DEBUG:
                print("Channel %d: Transmitted? %s " % (ch, dok))

def WaitTrigAndSendClock():
    """   """
    global gFirstevt, gReadingOut

    if DEBUG:
        print("WaitTrigAndSendClock Executed.")
        # Print Statements!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if AreCardsPowered():
        # Create SPI Link HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        if gFirstEvt:
            gFirstEvt = False

        if DEBUG:
            print("Waiting for Trigger...")

        # Setting gReadingOut False Enables Force Triggers
        gReadingOut = False

        # Wait for FPGA Data Ready Flag
        while(GPIO.input(7) == 0):
            # Perform Nesscary Functions While Waiting
            if gOpenCommWin or gCheckTemp:
                # DEBUG!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                return

        # Data is Ready
        gReadingOut = True
    else:
        gReadingOut = False
        gFirstEvt   = False



if __name__=="__main__":
    if DEBUG:
        print("System Starting...")

#def SetConfigAndMakeOuputfile(): # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    if DEBUG:
        print("SetConfigAndMakeOuputfile Executed.")

    # WD RESET !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    GPIO.output(12, False)  # Enable Thermal Triggers
    GPIO.output(13, False)  # Execute Forced Trigger
    # HB Trigger HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    time.sleep(0.2)

    # Load & Set Board Configurations
    LoadDEFCONF()
    if DEBUG:
        print("Configuration File Loaded.")

    SetSstDACs(bus)  # I2C Set SST Thresholds

    # Set Pins to Configuration Settings [DATA TAKING PHASE]
    GPIO.output(12, bool(C.ConfigFrame['fEnableThermTrig']))              # Enable Thermal Triggers
    #GPIO.output(13, bool(C.ConfigFrame['fEnableThermTrig']))              # Execute Forced Trigger
    GPIO.output(33, bool(C.ConfigFrame['PowerOnFor'] & kCardDatTak))      # Card/ Data Taking Power
    GPIO.output(36, bool(C.ConfigFrame['PowerOnFor'] & kAmpsDatTak))      # Amp Power
    GPIO.output(40, bool(C.ConfigFrame['PowerOnFor'] & kIridDatTak))      # Iridium Power



    while(True):
        if DEBUG:
            print("Starting Main Loop...")

        # RESET WATCHDOG HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        if DEBUG:
            print("gFirstEvt = %s" % (gFirstEvt))
            print("gReadingOut = %s" % (gReadingOut))

        if gFirstEvt:
            # TIMER RESET HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            if not (C.ConfigFrame['fRunMode'] & kSkipTrgStartReset):
                if DEBUG:
                    print("----------------------------------------------------")
                    print("First Event Trigger Start Reset.")

                # Reset Chips
                GPIO.output(8, True)
                GPIO.output(8, False)

            else:
                if DEBUG:
                    print("----------------------------------------------------")
                    print("First Event Trigger Start Reset. [SKIPPED]")

        # Wait for Trigger
        GPIO.output(31, False)
        WaitTrigAndSendClock()

        if gReadingOut:






