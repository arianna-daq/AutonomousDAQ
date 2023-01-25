"""
SnConstants.py

Python module containing constant values or arrays that are used by various
different programs including the main.py.

Author: Manuel Pasqual Paul [mppaul@uci.edu]
Last Updated: 08-11-22f
"""

import numpy as np
from SnBitUtils import BITS_IN_CHAR, BIT
from SnPreCompOptions import CHIPBOARD, SST8CH

# Select the MAC Addr for each and every RPi board
DefaultMacAddr  = np.array([0x00, 0x02, 0xAA, 0xAA, 0xAA, 0xAA ]) # Lab Testing MAC Addr
#DefaultMacAddr  = np.array([0x00, 0x02, 0xBB, 0xBB, 0xBB, 0xBB ]) # Lab Testing MAC Addr

kIridPwrFromAfar = False         # True if Iridium and Afar are on same relay, False if not
kBStime          = 946713600     # Unix Time for 1/1/2000 00:00:00 UTC

kNplasV1             = 5         # Preserve i/o version sizes
kNsampsSst           = 256       # Number of Samples per Waveform
kNchanDacsSst        = 2         # Number of DACs per CH
kNchansEightAnt      = 8         # 8 CH Board
kNchipsSst8ch        = 2         # Number of SST Chips for 8 CH Board
kNcomms              = 1         # Number of Communications Types Available
kNvoltsAve           = 500       # Number of Voltage Samples to Average
kAbsMaxTimer         = 1800      # Max Time [seconds] a Counter/ Timer can do
kDefTimeoutMin       = 1         # [minutes] Used in Case min range needs enforcing
kDefTimeoutSafe      = 3         # [minutes] Used in Case a Clock Error or max range needs enforcing
kCommWinLongPrdTk    = 300       # [seconds] Check if it's Time for a CommWin every X seconds
kMaxConsecCommFails  = 75        # Number of Times a CommWin can Fail before RPi Resets

# Safety Nets
kMaxFirstSeq             = 25000     # Max Sequence Number
kMinForcePer             = 0.05      # [seconds] Max Force Trigger Rate
kMaxThrottlePerMs        = 60000     # [milliseconds] Max Time between Thermal Triggers
kMaxBatVoltLowPwr        = 25000     # [ADCs] Max Battery Voltage in Low Power Mode
kMinCommWinPeriod        = 120       # [seconds] Min Time between CommWin
kMaxCommWinPeriod        = 259200    # [seconds] Max Time between CommWin
kMinCommWinDur           = 600       # [seconds] Min CommWin Duration \\ N >= Ncomms * listen / connect timeout
kMaxWatchDogPer          = 3600      # [seconds] Max Time before WatchDog Reset
kMinWatchDogPer          = 300       # [seconds] Min Time before WatchDog Reset
kMinSingleFreqSuppRatio  = 26        # [0.1] Min Cut Value (L1 < 0.1)
kMaxSingleFreqSuppRatio  = 255       # [1.0] Min Cut Value (L1 < 1.0)
kDefSingleFreqSuppRatio  = 77        # [0.3] Default Value (L1 = 0.3)

kTotSampsSst8ch   = kNchansEightAnt * kNsampsSst
kTotDacsSst8ch    = kNchansEightAnt * kNchanDacsSst
kNstopBytesSst8ch = kNchipsSst8ch * (kNsampsSst / BITS_IN_CHAR)
kNchans           = kNchansEightAnt
kNsamps           = kNsampsSst
kNchanDacs        = kNchanDacsSst
kNstopBytes       = kNstopBytesSst8ch
kTotSamps         = kNchans * kNsamps
kTotDacs          = kNchans * kNchanDacs

kNumLTC2657s      = 2             # Number of DAC Chips per Board
kChansPerLTC2657  = 4             # Number of CHs Assigned per DAC
kLTC2657Addr      = [0x41, 0x32]  # LTC2657 Slave Addr \\ BIT Form: [10000010, 01100100]
kUpdateDacCmd     = 3             # LTC2657 Write Command \\ BIT Form: [0011]
kMaxDacSetTries   = 3             # Try to Set DACs N Times
kMaxTempReadTries = 3             # Try to Update Temp Reading N Times

# RunMode Options
kSingleSeq              = BIT(0) # if 0, infinite sequences
kCountPower             = BIT(1) # if 0, count events
kDualThresh             = BIT(2) # if 0, single sided thresholds on SST
kDiffTrig               = BIT(3) # if 0, send result of each comparator on SST
kLowPwrSBDonly          = BIT(4) # if 0, low power afar / sbd power settings same as normal.if 1, afar off and sbd on during low power mode
kRunSeqListOneCommWin   = BIT(5) # if 0, only clear run / seq list after files sent from it
kIgnoreSDcard           = BIT(6) # if 0, read / write data to SD card as normal.if 1, function as though no SD card is present
kCommPowerSimple        = BIT(7) # if 0, comm periphs powered as needed during comm win.if 1, power adjusted once at start / finish of comm win
kCommWinEachEvent       = BIT(8) # if 0, comm windows only after comm period of seconds. if 1, comm winodows also after each event that qualifies for saving to SD card
kSkipTrgStartReset      = BIT(9) # if 0, the digitizer (SST) is reset when the mbed starts waiting for triggers. if 0, no reset occurs, which can cause an immediate readout if the chip had triggered before the mbed was ready

# Communication Types
kIridCommType           = BIT(0) # if 1, communicating with Iridium is active

# L Filter Options
kSingleFreqSupp         = BIT(0) # if 1, activate single frequency filter better known as L1
kNeuralNetFilter        = BIT(1) # if 1, activate neural net filter

# Power On Options
kAmpsDatTak             = BIT(0)
kCardDatTak             = BIT(1)
kIridDatTak             = BIT(2)
kAmpsComWin             = BIT(3)
kCardComWin             = BIT(4)
kIridComWin             = BIT(5)

# Communication Send Data Options
kDefaultSendData            = BIT(0)
kAllFiles                   = BIT(1)
kCloseOnTimeout             = BIT(2)
kDeleteIfReceived           = BIT(3)
kForceSBDtoSendFileData     = BIT(4)
kHandshakeBeforeSendData    = BIT(5)
kSendRunSeqList             = BIT(6)
kStatSendConf               = BIT(7)
kStatSendTrgTim             = BIT(8)
kStatSendPwrDat             = BIT(9)
kStatSendEvent              = BIT(10)
kStatSendHtbt               = BIT(11)
kStatSendTmpDat             = BIT(12)

class ETrigBit:
    '''A "Look Up Table: for the Locations and Values of Event Frame Variables.
    Each Variable Vit is one Bit of a 16 Bit Variable fTrigBits used in
    SnEventFrame.py. fTrigBits is used as a Program Wide "Storage" for Event
    Frame Settings.'''

    kThermal         = BIT(0) # Thermal Trigger  \\ BIT Form: [0000000000000001]
    kForced          = BIT(1) # Forced Trigger   \\ BIT Form: [0000000000000010]
    kExternal        = BIT(2) # External Trigger \\ BIT Form: [0000000000000100]
    kSingleFreqSupp  = BIT(3) # L1 Filter Active \\ BIT Form: [0000000000001000]
    # Bit 4 in fTrigBits not used yet
    kL1Scaledown     = BIT(5) # Whether Event is written due to L1 Scaledown     \\ BIT Form: [0000000000100000]
    kL1TrigApplied   = BIT(6) # Whether Event is Thrown Away due to L1 Filter    \\ BIT Form: [0000000001000000]
    kAdcToRPiflag    = BIT(7) # Data Transfer from Cards to RPi was too long     \\ BIT Form: [0000000010000000]

class EL1TrigStatus:
    '''All possible results for L1 filter'''

    kL1Fail              = 0
    kL1Pass              = 1
    kL1UnableToProcess   = 2