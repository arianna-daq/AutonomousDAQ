"""
SnConstants.py

Python module containing constant values or arrays that are used by various
different programs including the main.py.

Author: Manuel Pasqual Paul [mppaul@uci.edu]
Last Updated: 08-11-22
"""

import numpy as np
from SnBitUtils import BITS_IN_CHAR
from SnBitUtils import BIT
from SnPreCompOptions import CHIPBOARD, SST8CH, SST4CH

# Select the MAC Addr for each and every RPi board
DefaultMacAddr  = np.array([0x00, 0x02, 0xAA, 0xAA, 0xAA, 0xAA ]) # Lab Testing MAC Addr
#DefaultMacAddr  = np.array([0x00, 0x02, 0xBB, 0xBB, 0xBB, 0xBB ]) # Lab Testing MAC Addr

IridPwrFromAfar = False         # True if Iridium and Afar are on same relay, False if not
BStime          = 946713600     # Unix Time for 1/1/2000 00:00:00 UTC

NplasV1             = 5         # Preserve i/o version sizes
NsampsSst           = 256       # Number of Samples per Waveform
NchanDacsSst        = 2         # Number of DACs per CH
NchansFourAnt       = 4         # 4 CH Board
NchansEightAnt      = 8         # 8 CH Board
NchipsSst4ch        = 1         # Number of SST Chips for 4 CH Board
NchipsSst8ch        = 2         # Number of SST Chips for 8 CH Board
Ncomms              = 1         # Number of Communications Types Available
NvoltsAve           = 500       # Number of Voltage Samples to Average
AbsMaxTimer         = 1800      # Max Time [seconds] a Counter/ Timer can do
DefTimeoutMin       = 1         # [minutes] Used in Case min range needs enforcing
DefTimeoutSafe      = 3         # [minutes] Used in Case a Clock Error or max range needs enforcing
CommWinLongPrdTk    = 300       # [seconds] Check if it's Time for a CommWin every X seconds
MaxConsecCommFails  = 75        # Number of Times a CommWin can Fail before RPi Resets

# Safety Nets
MaxFirstSeq = 25000 # Max Sequence Number
MinForcePer = 0.05  # [seconds] Max Force Trigger Rate
MaxThrottlePerMs        = 60000     # [milliseconds] Max Time between Thermal Triggers
MaxBatVoltLowPwr        = 25000     # [ADCs] Max Battery Voltage in Low Power Mode
MinCommWinPeriod        = 120       # [seconds] Min Time between CommWin
MaxCommWinPeriod        = 259200    # [seconds] Max Time between CommWin
MinCommWinDur           = 600       # [seconds] Min CommWin Duration \\ N >= Ncomms * listen / connect timeout
MaxWatchDogPer          = 3600      # [seconds] Max Time before WatchDog Reset
MinWatchDogPer          = 300       # [seconds] Min Time before WatchDog Reset
MinSingleFreqSuppRatio  = 26        # [0.1] Min Cut Value (L1 < 0.1)
MaxSingleFreqSuppRatio  = 255       # [1.0] Min Cut Value (L1 < 1.0)
DefSingleFreqSuppRatio  = 77        # [0.3] Default Value (L1 = 0.3)

TotSampsSst4ch  = NchansFourAnt  * NsampsSst
TotSampsSst8ch  = NchansEightAnt * NsampsSst
TotDacsSst4ch   = NchansFourAnt  * NchanDacsSst
TotDacsSst8ch   = NchansEightAnt * NchanDacsSst

NstopBytesSst4ch = NchipsSst4ch * (NsampsSst / BITS_IN_CHAR)
NstopBytesSst8ch = NchipsSst8ch * (NsampsSst / BITS_IN_CHAR)

if CHIPBOARD == SST4CH:
    Nchans          = NchansFourAnt
    Nsamps          = NsampsSst
    NchanDacs       = NchanDacsSst
    NstopBytes      = NstopBytesSst4ch
    NumLTC2657s     = 1                 # Number of DAC Chips per Board
    ChansPerLTC2657 = 4                 # Number of CHs Assigned per DAC
    LTC2657Addr     = np.array([115 << 1])  # LTC2657 Slave Addr \\ BIT Form: [11100110]
    UpdateDacCmd    = 3                 # LTC2657 Write Command \\ BIT Form: [0011]
    MaxDacSetTries  = 3                 # Try to Set DACs N Times

elif CHIPBOARD == SST8CH:
    Nchans          = NchansEightAnt
    Nsamps          = NsampsSst
    NchanDacs       = NchanDacsSst
    NstopBytes      = NstopBytesSst8ch
    NumLTC2657s     = 2                 # Number of DAC Chips per Board
    ChansPerLTC2657 = 4                 # Number of CHs Assigned per DAC
    LTC2657Addr     = np.array([65 << 1, 50 << 1])  # LTC2657 Slave Addr \\ BIT Form: [10000010, 01100100]
    UpdateDacCmd    = 3                 # LTC2657 Write Command \\ BIT Form: [0011]
    MaxDacSetTries  = 3                 # Try to Set DACs N Times

else:
    raise ("CHIPBOARD Not Defined in SnPreCompOptions.py")

TotSamps    = Nchans * Nsamps
TotDacs     = Nchans * NchanDacs

class ETrigBit:
    '''A "Look Up Table: for the Locations and Values of Event Frame Variables.
    Each Variable Vit is one Bit of a 16 Bit Variable fTrigBits used in
    SnEventFrame.py. fTrigBits is used as a Program Wide "Storage" for Event
    Frame Settings.'''

    Thermal         = BIT(0) # Thermal Trigger  \\ BIT Form: [0000000000000001]
    Forced          = BIT(1) # Forced Trigger   \\ BIT Form: [0000000000000010]
    External        = BIT(2) # External Trigger \\ BIT Form: [0000000000000100]
    SingleFreqSupp  = BIT(3) # L1 Filter Active \\ BIT Form: [0000000000001000]
    # Bit 4 in fTrigBits not used yet
    L1Scaledown     = BIT(5) # Whether Event is written due to L1 Scaledown     \\ BIT Form: [0000000000100000]
    L1TrigApplied   = BIT(6) # Whether Event is Thrown Away due to L1 Filter    \\ BIT Form: [0000000001000000]
    AdcToRPiflag    = BIT(7) # Data Transfer from Cards to RPi was too long     \\ BIT Form: [0000000010000000]

class EL1TrigStatus:
    '''All possible results for L1 filter'''

    L1Fail              = 0
    L1Pass              = 1
    L1UnableToProcess   = 2