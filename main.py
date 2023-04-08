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

# Initialize and Assign IO pins
###############################
bus = SMBus(1)            # I2C Pins 3, 5
GPIO.setmode(GPIO.BOARD)  # Sets GPIO Function Input Format [Pin or GPIO]

# Input Pins
GPIO.setup(7, GPIO.IN)  # Data Ready Flag

# Output Pins
GPIO.setup(8, GPIO.OUT, initial=False)   # Reset Chips
GPIO.setup(12, GPIO.OUT, initial=False)  # Enable Thermal Triggers
GPIO.setup(13, GPIO.OUT, initial=False)  # Execute Forced Trigger
GPIO.setup(15, GPIO.OUT, initial=True)   # FPGA Differential Select
GPIO.setup(16, GPIO.OUT, initial=True)   # Dual Threshold Select !!!!!!!!!!!!!!!!!!!!!!!!!!
GPIO.setup(26, GPIO.OUT, initial=False)  # Majority Logic Low Bit
GPIO.setup(29, GPIO.OUT, initial=False)  # Majority Logic High Bit
GPIO.setup(31, GPIO.OUT, initial=False)  # Reading Out Data Select
GPIO.setup(33, GPIO.OUT, initial=False)  # Card/ Data Taking Power
GPIO.setup(36, GPIO.OUT, initial=False)  # Amp Power
GPIO.setup(40, GPIO.OUT, initial=False)  # Iridium Power

# USED PINS
# GPIO.setup(35, GPIO.IN)    # Power Probe 1 [UNUSED Pin]
# GPIO.setup(37, GPIO.IN)    # Power Probe 2 [UNUSED Pin]
# GPIO.setup(38, GPIO.OUT)   # UNUSED Pin

# Pin 32 Temp Probe [No IO Initialization Needed]
# See README for More Details Regarding P32.
# GND Pins 6, 9, 14, 20, 25, 30,34, 39

# Initialize Flag Variables
###########################
gFirstEvt     = True     # First Event of Sequence
gReadingOut   = False    # Readout Data from FPGA
gOpenCommWin  = False    # Open Comm Window
gCheckTemp    = False    # Check Temperature
gCardsPowered = False    # Cards Powered On

# Essential Functions
#####################



def SetPower(isCommWin): # MISSING WD
    """   """

    if DEBUG:
        print("Set Power Executed: isCommWin? %s" % (isCommWin))
        print("Power Config Byte: %s" % (SnConfigFrame().PowerMode()))
        print("IsPoweredFor kCardDatTak: %s" % (bool(SnConfigFrame().IsPoweredFor(kCardDatTak))))
        print("IsPoweredFor kAmpsDatTak: %s" % (bool(SnConfigFrame().IsPoweredFor(kAmpsDatTak))))
        print("IsPoweredFor kIridDatTak: %s" % (bool(SnConfigFrame().IsPoweredFor(kIridDatTak))))
        print("IsPoweredFor kCardComWin: %s" % (bool(SnConfigFrame().IsPoweredFor(kCardComWin))))
        print("IsPoweredFor kAmpsComWin: %s" % (bool(SnConfigFrame().IsPoweredFor(kAmpsComWin))))
        print("IsPoweredFor kIridComWin: %s" % (bool(SnConfigFrame().IsPoweredFor(kIridComWin))))

    if isCommWin:
        cardpb = kCardComWin
        ampspb = kAmpsComWin
        iridpb = kIridComWin
    else:
        cardpb = kCardDatTak
        ampspb = kAmpsDatTak
        iridpb = kIridDatTak

    cardToOn = SnConfigFrame().IsPoweredFor(cardpb)
    ampsToOn = SnConfigFrame().IsPoweredFor(ampspb)
    iridToOn = SnConfigFrame().IsPoweredFor(iridpb)

    if not cardToOn:
        GPIO.output(33, False)
        if DEBUG:
            print("Powering Down Cards")

    if cardToOn:
        GPIO.output(33, True)
        if DEBUG:
            print("Powering Up Cards")

    if not ampsToOn:
        GPIO.output(36, False)
        if DEBUG:
            print("Powering Down Amps")

    if ampsToOn:
        GPIO.output(36, True)
        if DEBUG:
            print("Powering Up Amps")

    if not iridToOn:
        GPIO.output(40, False)
        if DEBUG:
            print("Powering Down Iridium")

    if iridToOn:
        GPIO.output(40, True)
        if DEBUG:
            print("Powering Up Iridium")

    # WAIT STATEMENT
    if DEBUG:
        print("Power Set; CommWin?: %s, ConfigByte: %s, Card: %s, Amps: %s, Irid: %s" %
              (bool(isCommWin), SnConfigFrame().PowerMode(), GPIO.input(33),
               GPIO.input(36), GPIO.input(40)))


def AreCardsPowered(checkPin):
    """Checks P33 Status. P33 [Output] Enables Power to Cards. If checkPin is True,
    Update gCardsPowered. If False, Use Old Value/ No Update."""

    global gCardsPowered

    if DEBUG:
        print("Executing ArCardsPowered?")
        print("CALL: Cards Powered?  %s" % (gCardsPowered))

    # Take New Measurement of P33
    if checkPin:
        gCardsPowered = (GPIO.input(33))

    if DEBUG:
        print("RETURN: Cards Powered?  %s" % (gCardsPowered))

    return gCardsPowered

def SetSstDACs(bus):
    """Sends the High and Low Thresholds to the LTC2657 DAC Chip via I2C."""

    # Init Variables
    dadr, dv, dn = 0, 0, 0
    LSB, MSB = 0, 0

    if DEBUG:
        print("Sending DAC Thresholds")

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


def LoadSetDEFCONF():
    """   """

    # Block Triggers during Configuration
    GPIO.output(12, False) # Thermal Trigger
    GPIO.output(13, False) # Force Trigger
    # HB set 0

    LoadDEFCONF()

    # COMMS CHECKS

    if AreCardsPowered(True):
        # Set Highest Maj Logic During Configuration
        GPIO.output(26, True) # MajLog Low Bit
        GPIO.output(29, True) # MajLog High Bit

        # I2C Set SST Thresholds
        SetSstDACs(bus)

        # WAIT TIMING

    else:
        if DEBUG:
            print("Cards OFF, Skipping DAC Set")

    # Set Pins to Config Settings
    GPIO.output(12, bool(SnConfigFrame().EnableThermTrig()))
    GPIO.output(15, bool(SnConfigFrame().IsRunMode(kDiffTrig)))
    GPIO.output(16, bool(SnConfigFrame().IsRunMode(kDualThresh)))

    HighBit, LowBit = SnConfigFrame().GetMajLog()
    GPIO.output(26, LowBit)   # MajLog Low Bit
    GPIO.output(29, HighBit)  # MajLog High Bit

    if DEBUG:
        print("EnableThermTrig: %s" % (bool(GPIO.input(12))))
        print("DiffTrig: %s" % (bool(GPIO.input(15))))
        print("DualThreshold: %s" % (bool(GPIO.input(16))))
        print("Majority Logic: %s" % (SnConfigFrame().ConfigFrame['fNumCardsMajLog']))
        print("MajLog LowBit: %s, HighBit: %s" % (LowBit, HighBit))


    # MAKE OUTPUT FILE
    # RESET TICKERS
    # WD KICK/ Wait

    if DEBUG:
        print("Configuration Complete.")



def WaitTrigAndSendClock(): # MISSING SPI SETTINGS
    """Secondary Loop under Main Loop. Waits for Trigger [P7] or Flags to
    Initiate Next Process. Flags Indicate Priority Functions Open Comms Window
    [gOpenCommWin] and Check Temperature [gCheckTemp]."""

    global gFirstEvt, gReadingOut, gOpenCommWin

    if DEBUG:
        print("WaitTrigAndSendClock Executed")
        print("Wait Trig PW Status; ConfigByte: %s, Card: %s, Amps: %, Irid: %s" %
              (SnConfigFrame().PowerMode(), GPIO.input(33), GPIO.input(36), GPIO.input(40)))
        print("Are Cards Powered?: %s" % (AreCardsPowerd(False)))

    if AreCardsPowered(False):
        # Create SPI Link HERE

        if gFirstEvt:
            gFirstEvt = False

        if DEBUG:
            print("Waiting for Trigger...")

        # Setting gReadingOut False Enables Force Triggers
        gReadingOut = False

        # Wait for FPGA Data Ready Flag
        while(GPIO.input(7) == False):

            # Perform Priority Functions While Waiting
            if gOpenCommWin or gCheckTemp:
                print("Priority Function Flag Triggered")
                print("gOpenCommWin: %s, gCheckTemp: %s" % (gOpenCommWin, gCheckTemp))
                return

        if DEBUG:
            print("FPGA Data Ready Flag [P7] Triggered")

        # Data is Ready
        gReadingOut = True
    else:
        gReadingOut = False
        gFirstEvt   = False

########################################################################
#                              MAIN CODE                               #
########################################################################

if __name__=="__main__":
    if DEBUG:
        print("System Starting...")
        #print("Local Time: %s" % (time.localtime()))
        print("Startup Power; Card: %s, Amps: %s, Irid: %s" %
              (bool(GPIO.input(33)), bool(GPIO.input(36)), bool(GPIO.input(40))))

    # WatchDog Reset, Comms Settings, MAC Addr, Timing Settings, Tickers and Clocks

    # Load & Set Board Configurations
    LoadSetDEFCONF()


    if DEBUG:
        print("Configuration File Loaded.")

    # Turn Off Comms, Turn On Cards/ Amps (Based on Config)
    SetPower(False)

    if DEBUG:
        print("Run Mode")
        print("IsSingleSeqMode: %s" % (bool(SnConfigFrame().IsRunMode(kSingleSeq))))
        print("IsCountPowerReading: %s" % (bool(SnConfigFrame().IsRunMode(kCountPower))))
        print("IsDualThresholdMode: %s" % (bool(SnConfigFrame().IsRunMode(kDualThresh))))
        print("IsDifferentialTrigMode: %s" % (bool(SnConfigFrame().IsRunMode(kDiffTrig))))
        print("IsSBDonlyLowPWRMode: %s" % (bool(SnConfigFrame().IsRunMode(kLowPwrSBDonly))))
        print("IsRunSeqListOneCommWinOnly: %s" % (bool(SnConfigFrame().IsRunMode(kRunSeqListOneCommWin))))
        print("IsIgnoringSDcard: %s" % (bool(SnConfigFrame().IsRunMode(kIgnoreSDcard))))
        print("IsCommPowerSimple: %s" % (bool(SnConfigFrame().IsRunMode(kCommPowerSimple))))
        print("Executing OpenCommWin")

    # OPEN COMM WINDOW CODE HERE/ SPI CODE

    AreCardsPowered(True)
    # Time Between events, Zerod.
    ETms = 0


    while(True):
        if DEBUG:
            print("Starting Main Loop...")

        # RESET WATCHDOG HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        if DEBUG:
            print("gFirstEvt = %s" % (gFirstEvt))
            print("gReadingOut = %s" % (gReadingOut))

        if gFirstEvt:
            # TIMER RESET HERE !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            if not (SnConfigFrame().ConfigFrame['fRunMode'] & kSkipTrgStartReset):
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







