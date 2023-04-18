# python main.py
from time import time
import numpy as np
from smbus import SMBus
import RPi.GPIO as GPIO
import spidev
from SnConstants import *
from SnPreCompOptions import *
from SnTempFrame import SnTempFrame, UpdateTemperature
from SnConfigFrame import SnConfigFrame, LoadDEFCONF
from SnTempFrame import *
from Watchdog import Watchdog
from threading import Timer

# Get Start Up Time
gPowerOnTime = time()

# Start Watchdog Immediately
Watchdog().Starter(WDFAILSAFE)

# MAC ADDRESS GOES HERE

# Initialize and Assign IO pins
###############################
bus = SMBus(1)            # I2C Pins 3, 5
GPIO.setmode(GPIO.BOARD)  # Sets GPIO Function Input Format [Pin or GPIO]

spi = spidev.SpiDev(0, 0)   # Uses /dev/spidev0.0 [SPI Pins 19, 21, 23, 24]
spi.max_speed_hz = 10000000 # Set Max SPI Speed [Max Limit: 32MHz]

# Pin Shortcuts
DataReady       = 7
ResetChips      = 8
ThermTrigEnable = 12
ForcedTrig      = 13
DiffSelect      = 15
AndOrSelect     = 16
HeartbeatTrig   = 22
MajorLowBit     = 26
MajorHighBit    = 29
ReadOutSelect   = 31
CardPower       = 33
AmpPower        = 36
IridPower       = 40

# Input Pins
GPIO.setup(DataReady, GPIO.IN)  # Data Ready Flag

# Output Pins
GPIO.setup(ResetChips, GPIO.OUT, initial=False)       # Reset Chips
GPIO.setup(ThermTrigEnable, GPIO.OUT, initial=False)  # Enable Thermal Triggers
GPIO.setup(ForcedTrig, GPIO.OUT, initial=False)       # Execute Forced Trigger
GPIO.setup(DiffSelect, GPIO.OUT, initial=True)        # FPGA Differential Select
GPIO.setup(AndOrSelect, GPIO.OUT, initial=True)       # Dual Threshold Select
GPIO.setup(HeartbeatTrig, GPIO.OUT, initial=False)    # Heartbeat Trigger
GPIO.setup(MajorLowBit, GPIO.OUT, initial=False)      # Majority Logic Low Bit
GPIO.setup(MajorHighBit, GPIO.OUT, initial=False)     # Majority Logic High Bit
GPIO.setup(ReadOutSelect, GPIO.OUT, initial=False)    # Reading Out Data Select
GPIO.setup(CardPower, GPIO.OUT, initial=False)        # Card/ Data Taking Power
GPIO.setup(AmpPower, GPIO.OUT, initial=False)         # Amp Power
GPIO.setup(IridPower, GPIO.OUT, initial=False)        # Iridium Power

# USED PINS
# GPIO.setup(18, GPIO.OUT)   # USUSED Pin
# GPIO.setup(27, GPIO.OUT)   # USUSED Pin [NOT GPIO]
# GPIO.setup(28, GPIO.OUT)   # USUSED Pin [NOT GPIO]
# GPIO.setup(35, GPIO.IN)    # Power Probe 1 [UNUSED Pin]
# GPIO.setup(37, GPIO.IN)    # Power Probe 2 [UNUSED Pin]
# GPIO.setup(38, GPIO.OUT)   # UNUSED Pin

# SBD Comms Pins 10, 11
# Pin 32 Temp Probe [No IO Initialization Needed]
# See README for More Details Regarding P32.
# GND Pins 6, 9, 14, 20, 25, 30, 34, 39
# VCC Related Pins 1, 2, 4, 17

# Initialize Global Variables
###########################
gForceticker     = None     # Force Trigger Ticker
gHeartbeatTicker = None     # Heartbeat Trigger Ticker
gTempCheckTicker = None     # Check Temperature Ticker
gCommWinTicker   = None     # Communication Window Ticker
gAllTrgTimer     = None     # Time between Triggers
gTrgLiveTimer    = None     # Elasped Time since Seqence Started

gFirstEvt     = True     # First Event of Sequence?
gReadingOut   = False    # Readed Data from FPGA?
gOpenCommWin  = False    # Open Comm Window?
gCommWinOpen  = False    # Is Comm Window Open?
gCheckTemp    = False    # Check Temperature?
gCardsPowered = False    # Cards Powered On?
gForcedTrig   = False    # Force Trigger Bit Flip?
gHrtbtFired   = False    # Heartbeat Sent?

gEvtNum           = 0   # Number of Events Written
gNumThmTrigs      = 0   # Number of Thermal Triggers
gNumFrcTrig       = 0   # Number of Forced Triggers
gNumSavedEvts     = 0   # Number of Saved Events; (Differs from gEvtNum)
gL1ScaledownCount = 0   # Write an Event every X L1 fails
gLastHrtbt        = 0   # Last Heartbeat Time
gHrtbtNum         = 0   # Number of Heartbeat Triggers


# Essential Functions
#####################
def procForceTrigger():
    global gReadingOut, gCommWinOpen, gForcedTrig, gNumFrcTrig
    global CardPower, DataReady, ForcedTrig

    if not gReadingOut and not gCommWinOpen:
        if DEBUG:
            print("Processing Force Trigger")
            print("Force Trig Pin: %s, Cards Powered?: %s, Data Ready?: %s" % 
                  (GPIO.input(ForcedTrig), GPIO.input(CardPower), GPIO.input(DataReady))) 
            
        gForcedTrig = True
        gNumFrcTrig += 1

        GPIO.output(ForcedTrig, True)
        GPIO.output(ForcedTrig, False)

def procHeartbeat():
    global gReadingOut, gCommWinOpen, HeartbeatTrig
    global gLastHrtbt, gHrtbtFired, gHrtbtNum

    if not gReadingOut and not gCommWinOpen:
        if DEBUG:
            print("Processing Heartbeat Trigger")
        
        GPIO.output(HeartbeatTrig, True)
        GPIO.output(HeartbeatTrig, False)

        gLastHrtbt = time()
        gHrtbtFired = True
        gHrtbtNum += 1

def procTempCheck():
    global gCheckTemp

    gCheckTemp = True


def SetPower(isCommWin): # MISSING WD
    global CardPower, AmpPower, IridPower

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
        GPIO.output(CardPower, False)
        if DEBUG:
            print("Powering Down Cards")

    if cardToOn:
        GPIO.output(CardPower, True)
        if DEBUG:
            print("Powering Up Cards")

    if not ampsToOn:
        GPIO.output(AmpPower, False)
        if DEBUG:
            print("Powering Down Amps")

    if ampsToOn:
        GPIO.output(AmpPower, True)
        if DEBUG:
            print("Powering Up Amps")

    if not iridToOn:
        GPIO.output(IridPower, False)
        if DEBUG:
            print("Powering Down Iridium")

    if iridToOn:
        GPIO.output(IridPower, True)
        if DEBUG:
            print("Powering Up Iridium")

    # WAIT STATEMENT
    if DEBUG:
        print("Power Set; CommWin?: %s, ConfigByte: %s, Card: %s, Amps: %s, Irid: %s" %
              (bool(isCommWin), SnConfigFrame().PowerMode(), GPIO.input(CardPower),
               GPIO.input(AmpPower), GPIO.input(IridPower)))


def AreCardsPowered(checkPin):
    """Checks P33 Status. P33 [Output] Enables Power to Cards. If checkPin is True,
    Update gCardsPowered. If False, Use Old Value/ No Update."""

    global gCardsPowered, CardPower

    if DEBUG:
        print("Executing ArCardsPowered?")
        print("CALL: Cards Powered?  %s" % (gCardsPowered))

    # Take New Measurement of P33
    if checkPin:
        gCardsPowered = (GPIO.input(CardPower))

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
                    print("MSB: %s" % format(MSB, '08b'))
                    print("LSB: %s" % format(LSB, '08b'))

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
    global ThermTrigEnable, ForcedTrig, MajorHighBit, MajorLowBit
    global DiffSelect, AndOrSelect

    # Block Triggers during Configuration
    GPIO.output(ThermTrigEnable, False) # Thermal Trigger
    GPIO.output(ForcedTrig, False)      # Force Trigger
    # HB set 0

    LoadDEFCONF()

    # COMMS CHECKS

    if AreCardsPowered(True):
        # Set Highest Maj Logic During Configuration
        GPIO.output(MajorLowBit, True)  # MajLog Low Bit
        GPIO.output(MajorHighBit, True) # MajLog High Bit

        # I2C Set SST Thresholds
        SetSstDACs(bus)

        # WAIT TIMING

    else:
        if DEBUG:
            print("Cards OFF, Skipping DAC Set")

    # Set Pins to Config Settings
    GPIO.output(ThermTrigEnable, bool(SnConfigFrame().EnableThermTrig()))
    GPIO.output(DiffSelect, bool(SnConfigFrame().IsRunMode(kDiffTrig)))
    GPIO.output(AndOrSelect, bool(SnConfigFrame().IsRunMode(kDualThresh)))

    HighBit, LowBit = SnConfigFrame().GetMajLog()
    GPIO.output(MajorLowBit, LowBit)    # MajLog Low Bit
    GPIO.output(MajorHighBit, HighBit)  # MajLog High Bit

    if DEBUG:
        print("EnableThermTrig: %s" % (bool(GPIO.input(ThermTrigEnable))))
        print("DiffTrig: %s" % (bool(GPIO.input(DiffSelect))))
        print("DualThreshold: %s" % (bool(GPIO.input(AndOrSelect))))
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

    global gFirstEvt, gReadingOut, gOpenCommWin, DataReady

    if DEBUG:
        print("WaitTrigAndSendClock Executed")
        print("Wait Trig PW Status; ConfigByte: %s, Card: %s, Amps: %s, Irid: %s" %
              (SnConfigFrame().PowerMode(), GPIO.input(CardPower), GPIO.input(AmpPower), GPIO.input(IridPower)))
        print("Are Cards Powered?: %s" % (AreCardsPowered(False)))

    if AreCardsPowered(False):
        # Create SPI Link HERE

        if gFirstEvt:
            gFirstEvt = False

        if DEBUG:
            print("Waiting for Trigger...")

        # Setting gReadingOut False Enables Force Triggers
        gReadingOut = False

        # Wait for FPGA Data Ready Flag
        while(GPIO.input(DataReady) == False):

            # Perform Priority Functions While Waiting
            if gOpenCommWin or gCheckTemp:
                print("Priority Function Flag Triggered")
                print("gOpenCommWin: %s, gCheckTemp: %s" % (gOpenCommWin, gCheckTemp))
                return

        if DEBUG:
            print("FPGA Data Ready Flag [P7] Triggered: P7 %s" % (bool(GPIO.input(DataReady))))

        # Data is Ready
        gReadingOut = True
    else:
        gReadingOut = False
        gFirstEvt   = False

#def SaveEvent(ETms):

########################################################################
#                              MAIN CODE                               #
########################################################################

if __name__=="__main__":
    if DEBUG:
        print("System Starting...")
        #print("Local Time: %s" % (time.localtime()))
        print("Startup Power; Card: %s, Amps: %s, Irid: %s" %
              (bool(GPIO.input(CardPower)), bool(GPIO.input(AmpPower)), bool(GPIO.input(IridPower))))

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
                if DEBUG:
                    print("Reset Chips; Before Reset: %s" % (bool(GPIO.input(ResetChips))))

                GPIO.output(ResetChips, True)

                if DEBUG:
                    print("Reset Chips; True? Reset: %s" % (bool(GPIO.input(ResetChips))))
                
                GPIO.output(ResetChips, False)

                if DEBUG:
                    print("Reset Chips; After Reset: %s" % (bool(GPIO.input(ResetChips))))

            else:
                if DEBUG:
                    print("----------------------------------------------------")
                    print("First Event Trigger Start Reset. [SKIPPED]")

        # Wait for Trigger
        GPIO.output(ReadOutSelect, False)
        WaitTrigAndSendClock()

        test = False # TESTING PURPOSES

        if gReadingOut:
            if test:
                saved = SaveEvent(ETms) 
            else:
                # Got a Trigger, but DO NOT SAVE EVENT.

                if DEBUG:
                    print(">>>>>>> THROW EVENT AWAY!")
                # printf(" forced=%s, first=%s, "
                #     "etms=%g, throttle=%hu, etms>=thr=%s\r\n",
                #     (gForcedTrig ? "true" : "false"),
                #     (gFirstEvt ? "true" : "false"),
                #     etms, gConf.GetEvtThrtlPeriodMs(),
                #     (etms>=gConf.GetEvtThrtlPeriodMs() ? "true" : "false"));

                # Reset Chips
                if DEBUG:
                    print("Reset Chips; Before Reset: %s" % (bool(GPIO.input(ResetChips))))

                GPIO.output(ResetChips, True)

                if DEBUG:
                    print("Reset Chips; True? Reset: %s" % (bool(GPIO.input(ResetChips))))
                
                GPIO.output(ResetChips, False)

                if DEBUG:
                    print("Reset Chips; After Reset: %s" % (bool(GPIO.input(ResetChips))))







