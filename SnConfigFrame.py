from SnBitUtils import *
from SnConstants import *
from SnHeaderFrame import ConfigCode
from os.path import exists, getsize
import binascii as bas

DEBUG_SCF = False            # if True, prints debugging outputs

# Local Input Files
infn    = "./DEFCONF.DAT"

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

ConfSettings = {
    'ConfLabel'                     : 63,
    'Run'                           :  2,
    'FirstSeq'                      :  1,
    'EvtsPerSeq'                    :  2,
    'RunMode'                       :  2,
    'DACS'                          : 32,
    'NumCardsMajLog'                :  1,
    'ThermalTrigOn'                 :  1,
    'ForcedPeriod'                  :  3,
    'HeartbeatPeriod'               :  2,
    'ThrottlePeriodms'              :  2,
    'VoltCheckPeriod'               :  2,
    'TempCheckPeriodAndPower'       :  1,
    'CommWinSendData'               :  2,
    'CommWinPeriod'                 :  3,
    'CommWinDuration'               :  3,
    'CommWinConnectTOmins'          :  2,
    'CommWinListenTOmins'           :  2,
    'L1TrigEnable'                  :  1,
    'L1TrigsApplied'                :  1,
    'L1Scaledown'                   :  1,
    'L1SingleFreqSuppressRatio'     :  1,
    'PowerOnFor'                    :  1,
    'WatchdogPeriod'                :  2,
    'WvLoseLSB'                     :  1,
    'WvLoseMSB'                     :  1,
    'WvBaseline'                    :  1,
}

# Default Configuration
# Sets the Configuration of the DAQ if infn is not located.
DefaultConfig = {
    'flabel': 'Default_1230',
    'fRun': 0,
    'fFirstSeq': 0,
    'fEvtsPerSeq': 300,
    'fRunMode': kDualThresh | kDiffTrig | kRunSeqListOneCommWin,
    'fDACS': {
        0: [200, 40000],
        1: [200, 40000],
        2: [200, 40000],
        3: [200, 40000],
        4: [200, 40000],
        5: [200, 40000],
        6: [200, 40000],
        7: [200, 40000]
    },
    'fNumCardsMajLog'                   :    2,
    'fEnableThermTrig'                  :    0,
    'fForcedPeriod'                     :    0,
    'fHeartbeatPeriod'                  :    0,
    'fThrottlePeriod'                   :    0,
    'fVoltCheckPeriod'                  :  127,
    'fTempPeriod'                       :    0,
    'CommWinSendData'                   :    1,
    'CommWinPeriod'                     :  300,
    'CommWinDuration'                   :  600,
    'CommWinConnectTOmins'              : [3, kIridCommType],
    'CommWinListenTOmins'               : [3, kIridCommType],
    'L1TrigEnable'                      :  [kSingleFreqSupp],
    'L1TrigsApplied'                    : False,
    'L1Scaledown'                       :   50,
    'L1SingleFreqSuppressRatio'         :   77,
    'PowerOnFor'                        :   32,
    'WatchdogPeriod'                    : 1200,
    'WvLoseLSB'                         :    0,
    'WvLoseMSB'                         :    4,
    'WvBaseline'                        :    0
}

class SnConfigFrame:
    ConfigFrame = {
        'flabel'                      : 'None',
        'fRun'                        :   None,
        'fFirstSeq'                   :   None,
        'fEvtsPerSeq'                 :   None,
        'fRunMode'                    :   None,
        'fDACS'                       : {
                        0: [None, None],
                        1: [None, None],
                        2: [None, None],
                        3: [None, None],
                        4: [None, None],
                        5: [None, None],
                        6: [None, None],
                        7: [None, None]
                        },
        'fNumCardsMajLog'             :   None,
        'fEnableThermTrig'            :   None,
        'fForcedPeriod'               :   None,
        'fHeartbeatPeriod'            :   None,
        'fThrottlePeriod'             :   None,
        'fVoltCheckPeriod'            :   None,
        'fTempPeriod'                 :   None,
        'CommWinSendData'             :   None,
        'CommWinPeriod'               :   None,
        'CommWinDuration'             :   None,
        'CommWinConnectTOmins'        :   [None, None],
        'CommWinListenTOmins'         :   [None, None],
        'L1TrigEnable'                :   [None],
        'L1TrigsApplied'              :   None,
        'L1Scaledown'                 :   None,
        'L1SingleFreqSuppressRatio'   :   None,
        'PowerOnFor'                  :   None,
        'WatchdogPeriod'              :   None,
        'WvLoseLSB'                   :   None,
        'WvLoseMSB'                   :   None,
        'WvBaseline'                  :   None
    }

    def GetDAC(self, ch, dc):
        return SnConfigFrame().ConfigFrame['fDACS'][ch][dc]


def checkDEFCONF(infn):
    if not exists(infn):
        return False
    else:
        return True

def getConfLabel(byte):
    Temp = ''
    for i in byte:
        hTemp = format(i, 'x')
        if hTemp != '0':
            Temp += bas.a2b_hex("%s" % (hTemp.strip())).decode("ASCII").replace(';', '\n- ')
    return Temp

def SetDEFCONF(infn):
    fnSize = getsize(infn)
    SCF = SnConfigFrame().ConfigFrame
    with open(infn, 'rb') as RPC:
        if format(ord(RPC.read(1)), 'x') == format(ConfigCode, 'x'):
            ByteLen = int.from_bytes(RPC.read(2), "little")

            if (fnSize - 3) != ByteLen:
                SCF = DefaultConfig
                if DEBUG_SCF == True:
                    print("Expected DEFCONF length does not match the local DEFCONF.")
                    print("Switching from local DEFCONF to Default.")
                RPC.close()
                return

            for sett in ConfSettings:
                byte_data = RPC.read(ConfSettings[sett])

                if sett == 'ConfLabel':
                    SCF['flabel'] = getConfLabel(byte_data)

                if sett == 'Run':
                    SCF['fRun'] = int.from_bytes(byte_data, "little")

                if sett == 'FirstSeq':
                    SCF['fFirstSeq'] = int.from_bytes(byte_data, "little")

                if sett == 'EvtsPerSeq':
                    SCF['fEvtsPerSeq'] = int.from_bytes(byte_data, "little")

                if sett == 'RunMode':
                    SCF['fRunMode'] = int.from_bytes(byte_data, "little")

                if sett == 'DACS':
                    for i in range(kNchans):
                        SCF['fDACS'][i][0] = int.from_bytes(byte_data[0 +(4 * i):2 +(4 * i)], "little")
                        SCF['fDACS'][i][1] = int.from_bytes(byte_data[2 +(4 * i):4 +(4 * i)], "little")

                if sett == 'NumCardsMajLog':
                    SCF['fNumCardsMajLog'] = int.from_bytes(byte_data, "little")

                if sett == 'ThermalTrigOn':
                    SCF['fEnableThermTrig'] = bool(int.from_bytes(byte_data, "little"))

                if sett == 'ForcedPeriod':
                    SCF['fForcedPeriod'] = int.from_bytes(byte_data, "little")

    RPC.close()
    if DEBUG_SCF == True:
        for key, value in SCF.items():
            print(key, value)
def LoadDEFCONF():
    if checkDEFCONF(infn) == True:
        SetDEFCONF(infn)
        if DEBUG_SCF == True:
            print("Local DEFCONF file found.")
            print("Local DEFCONF loaded.")

    else:
        print("No local DEFCONF found.")
        SnConfigFrame().ConfigFrame = DefaultConfig
        if DEBUG_SCF == True:
            print("Default DEFCONF loaded.")

if __name__=="__main__":
    LoadDEFCONF()