from SnBitUtils import *
from SnConstants import *
from SnHeaderFrame import ConfigCode
from os.path import exists, getsize
import binascii as bas

# if True, prints debugging outputs
DEBUG_SCF = False
#DEBUG_SCF = True

# Local Input DEFCONF File
infn    = "./DEFCONF.DAT"

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
    'TempCheckPeriod'               :  1,
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
    'flabel'                            :    'Default_1230',
    'fRun'                              :    0,
    'fFirstSeq'                         :    0,
    'fEvtsPerSeq'                       :  300,
    'fRunMode'                          : kDualThresh | kDiffTrig,
    'fDACS'                             : {
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
    'CommWinSendData'                   :  kDefaultSendData,
    'CommWinPeriod'                     :  300,
    'CommWinDuration'                   :  600,
    'CommWinConnectTOmins'              : [3, kIridCommType],
    'CommWinListenTOmins'               : [3, kIridCommType],
    'L1TrigEnable'                      :    0,
    'L1TrigsApplied'                    : False,
    'L1Scaledown'                       :   50,
    'L1SingleFreqSuppressRatio'         :   77,
    'PowerOnFor'                        :  kIridComWin,
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
        'L1TrigEnable'                :   None,
        'L1TrigsApplied'              :   None,
        'L1Scaledown'                 :   None,
        'L1SingleFreqSuppressRatio'   :   None,
        'PowerOnFor'                  :   None,
        'WatchdogPeriod'              :   None,
        'WvLoseLSB'                   :   None,
        'WvLoseMSB'                   :   None,
        'WvBaseline'                  :   None
    }

    def EnableThermTrig(self):
        return bool(SnConfigFrame().ConfigFrame['fEnableThermTrig'])

    def GetDAC(self, ch, dc):
        return SnConfigFrame().ConfigFrame['fDACS'][ch][dc]

    def PowerMode(self):
        return format(SnConfigFrame().ConfigFrame['PowerOnFor'], '08b')

    def SetDefaultConfig(self):
        SnConfigFrame().ConfigFrame = DefaultConfig

    def IsPoweredFor(self, PowOption):
        return SnConfigFrame().ConfigFrame['PowerOnFor'] & PowOption

    def IsRunMode(self, RMOption):
        return SnConfigFrame().ConfigFrame['fRunMode'] & RMOption

    def GetMajLog(self):
        ML = format(SnConfigFrame().ConfigFrame['fNumCardsMajLog'], '02b')
        return bool(ML[1]), bool(ML[0])


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
            # NOTE: This Piece of Code Does Not Always Run in Local Versions of Python
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
                return False

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

                if sett == 'HeartbeatPeriod':
                    SCF['fHeartbeatPeriod'] = int.from_bytes(byte_data, "little")

                if sett == 'ThrottlePeriodms':
                    SCF['fThrottlePeriod'] = int.from_bytes(byte_data, "little")

                if sett == 'VoltCheckPeriod':
                    SCF['fVoltCheckPeriod'] = int.from_bytes(byte_data, "little")

                if sett == 'TempCheckPeriod':
                    SCF['fTempPeriod'] = int.from_bytes(byte_data, "little")

                if sett == 'CommWinSendData':
                    SCF['CommWinSendData'] = int.from_bytes(byte_data, "little")

                if sett == 'CommWinPeriod':
                    SCF['CommWinPeriod'] = int.from_bytes(byte_data, "little")

                if sett == 'CommWinDuration':
                    SCF['CommWinDuration'] = int.from_bytes(byte_data, "little")

                if sett == 'CommWinConnectTOmins':
                    SCF['CommWinConnectTOmins'][0] = int.from_bytes(byte_data[0:1], "little")
                    SCF['CommWinConnectTOmins'][1] = int.from_bytes(byte_data[1:2], "little")

                if sett == 'CommWinListenTOmins':
                    SCF['CommWinListenTOmins'][0] = int.from_bytes(byte_data[0:1], "little")
                    SCF['CommWinListenTOmins'][1] = int.from_bytes(byte_data[1:2], "little")

                if sett == 'L1TrigEnable':
                    SCF['L1TrigEnable'] = int.from_bytes(byte_data, "little")

                if sett == 'L1TrigsApplied':
                    SCF['L1TrigsApplied'] = int.from_bytes(byte_data, "little")

                if sett == 'L1Scaledown':
                    SCF['L1Scaledown'] = int.from_bytes(byte_data, "little")

                if sett == 'L1SingleFreqSuppressRatio':
                    SCF['L1SingleFreqSuppressRatio'] = int.from_bytes(byte_data, "little")

                if sett == 'PowerOnFor':
                    SCF['PowerOnFor'] = int.from_bytes(byte_data, "little")

                if sett == 'WatchdogPeriod':
                    SCF['WatchdogPeriod'] = int.from_bytes(byte_data, "little")

                if sett == 'WvLoseLSB':
                    SCF['WvLoseLSB'] = int.from_bytes(byte_data, "little")

                if sett == 'WvLoseMSB':
                    SCF['WvLoseMSB'] = int.from_bytes(byte_data, "little")

                if sett == 'WvBaseline':
                    SCF['WvBaseline'] = int.from_bytes(byte_data, "little")

    RPC.close()
    if DEBUG_SCF == True:
        for key, value in SCF.items():
            print(key, value)

def LoadDEFCONF():
    if checkDEFCONF(infn) == True:
        DEF_LOADED = SetDEFCONF(infn)
        if DEF_LOADED == True:
            if DEBUG_SCF == True:
                print("Local DEFCONF file found.")
                print("Local DEFCONF loaded.")

    elif DEF_LOADED == False:
        SnConfigFrame().ConfigFrame = DefaultConfig
        if DEBUG_SCF == True:
            print("Default DEFCONF loaded.")

if __name__=="__main__":
    LoadDEFCONF()