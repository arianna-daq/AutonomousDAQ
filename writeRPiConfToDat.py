"""
writeRPiConfToDat.py

Conversion program takes a RPi DEFCONF.TXT file and converts it to a .DAT file that is
compatible with the Raspberry Pi Code on the 8CH DAQ+.

Author: Manuel Pasqual Paul [mppaul@uci.edu]
Last Updated: 12-08-22
"""

import sys
import binascii as bas

def BIT(n):
    return 1 << n

ConfigCode = 0x40
Nchans = 8

RunMode = {
    "SingleSeq"             : BIT(0),
    "CountPower"            : BIT(1),
    "DualThresh"            : BIT(2),
    "DiffTrig"              : BIT(3),
    "LowPwrSBDonly"         : BIT(4),
    "RunSeqListOneCommWin"  : BIT(5),
    "IgnoreSDcard"          : BIT(6),
    "CommPowerSimple"       : BIT(7),
    "CommWinEachEvent"      : BIT(8),
    "SkipTrgStartReset"     : BIT(9)
}

CommWinSendData = {
    "DefaultSendData"           : BIT(0),
    "AllFiles"                  : BIT(1),
    "CloseOnTimeout"            : BIT(2),
    "DeleteIfReceived"          : BIT(3),
    "ForceSBDtoSendFileData"    : BIT(4),
    "HandshakeBeforeSendData"   : BIT(5),
    "SendRunSeqList"            : BIT(6),
    "StatSendConf"              : BIT(7),
    "StatSendTrgTim"            : BIT(8),
    "StatSendPwrDat"            : BIT(9),
    "StatSendEvent"             : BIT(10),
    "StatSendHtbt"              : BIT(11),
    "StatSendTmpDat"            : BIT(12)
}

L1TrigEnable = {
    "SingleFreqSupp"    : BIT(0),
    "NeuralNetFilter"   : BIT(1)
}

CommType = {
    "Iridium"   : BIT(0)
}

PowerMode = {
    "AmpsDatTak"    : BIT(0),
    "CardDatTak"    : BIT(1),
    "IridDatTak"    : BIT(2),
    "AmpsComWin"    : BIT(3),
    "CardComWin"    : BIT(4),
    "IridComWin"    : BIT(5)
}

BitArray = {
    "RunMode"           : 0,
    "DACS"              : {},
    "CommWinSendData"   : 0,
    "L1TrigEnable"      : 0,
    "PowerOnFor"        : 0
}

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

def SaveToDAT(inarr):
    HexArr = ''
    for call in ConfSettings:
        if ConfSettings[call] == 1:
            HexArr += format(inarr[call], '02X')

        elif ConfSettings[call] == 2:
            if call == 'CommWinListenTOmins' or call == 'CommWinConnectTOmins':
                for i in range(2):
                    HexArr += format(inarr[call][i], '02X')
            else:
               temp = format(inarr[call], '04X')
               HexArr += (temp[2:4] + temp[0:2])

        elif ConfSettings[call] == 3:
            temp = format(inarr[call], '06X')
            HexArr += (temp[4:6] + temp[2:4] + temp[0:2])

        elif call == 'ConfLabel':
            num = (63 - len(inarr[call]))
            for i in inarr[call]:
                HexArr += format(ord(i), 'x')

            for i in range(num):
                HexArr += format(0, '02X')

        elif call == 'DACS':
            for i in range(Nchans):
                for j in range(2):
                    temp = format(inarr[call][i][j], '04X')
                    HexArr += (temp[2:4] + temp[0:2])

    with open("DEFCONF.DAT", 'wb') as outfn:
        outfn.write(bas.unhexlify(format(ConfigCode, '02X')))
        temp = format(int(len(HexArr)/2), '04X')
        outfn.write(bas.unhexlify(temp[2:4] + temp[0:2]))
        outfn.write(bas.unhexlify(HexArr))
        outfn.close()

def GetConf(infn):
    with open("./DEFCONF.TXT") as RPC:
        lines = RPC.readlines()

        for line in lines:
            if (line != '\n' and  line[0] != '#'):
                call, value = line[:-1].split('=')

                if call == 'DAQchip':
                    if value in DAQchip:
                        BitArray['DAQchip'] = DAQchip[value]
                    else:
                        raise KeyError(str(value) + " is not a key for DAQchip.")

                elif call == 'ConfLabel':
                    if len(value) < 64:
                        BitArray['ConfLabel'] = str(value)
                    else:
                        BitArray['ConfLabel'] = str(value[:63])

                elif call == 'Run':
                    if 0 <= int(value) < 65536:
                        BitArray['Run'] = int(value)
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'FirstSeq':
                    if 0 <= int(value) < 256:
                        BitArray['FirstSeq'] = int(value)
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'EvtsPerSeq':
                    if 1 <= int(value) < 65536:
                        BitArray['EvtsPerSeq'] = int(value)
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'RunMode':
                    if value in RunMode:
                        BitArray['RunMode'] |= RunMode[value]
                    else:
                        raise KeyError(str(value) + " is not a key for RunMode.")

                elif call == 'DACS':
                    ch, HLDACS = value.split(" : ")
                    LowDac, HighDac = HLDACS.split(',')
                    if 0 <= int(HighDac) < 65536 and 0 <= int(LowDac) < 65536:
                        BitArray['DACS'][int(ch)] = [int(LowDac), int(HighDac)]
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'NumCardsMajLog':
                    if 1 <= int(value) <= 8:
                        BitArray['NumCardsMajLog'] = int(value)
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'ThermalTrigOn':
                    if value == 'False':
                        BitArray['ThermalTrigOn'] = 0
                    elif value == 'True':
                        BitArray['ThermalTrigOn'] = 1
                    else:
                        raise TypeError("ThermalTrigOn should be a bool type.")

                elif call == 'ForcedPeriod':
                    if 0.05 <= float(value) <= 1800 or float(value) == 0.0:
                        BitArray['ForcedPeriod'] = int(float(value)*100)
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'HeartbeatPeriod':
                    if 0 <= int(value) <= 1800:
                        BitArray['HeartbeatPeriod'] = int(value)
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'ThrottlePeriodms':
                    if 0 <= int(value) <= 1800:
                        BitArray['ThrottlePeriodms'] = int(value)
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'VoltCheckPeriod':
                    if 0 <= int(value) <= 1800:
                        BitArray['VoltCheckPeriod'] = int(value)
                    else:
                        raise ValueError(str(value) + " Value is not within range.")

                elif call == 'TempCheckPeriodAndPower':
                    if 0 <= int(value) <= 30:
                        BitArray['TempCheckPeriodAndPower'] = int(value)
                    else:
                        raise KeyError(str(value) + " Value is not within range or is not a key for Temperature Power.")

                elif call == 'CommWinPeriod':
                    if 120 <= int(value) <= 259200:
                        BitArray['CommWinPeriod'] = int(value)
                    else:
                        raise KeyError(str(value) + " Value is not within range.")

                elif call == 'CommWinDuration':
                    if 0 <= int(value) <= 86400:
                        BitArray['CommWinDuration'] = int(value)
                    else:
                        raise KeyError(str(value) + " Value is not within range.")

                elif call == 'CommWinSendData':
                    if value in CommWinSendData:
                        BitArray['CommWinSendData'] |= CommWinSendData[value]
                    else:
                        raise KeyError(str(value) + " is not a key for CommWinSendData.")

                elif call == 'L1TrigEnable':
                    if value in L1TrigEnable:
                        BitArray['L1TrigEnable'] = L1TrigEnable[value]
                    else:
                        raise KeyError(str(value) + " is not a key for L1TrigEnable.")

                elif call == 'L1TrigsApplied':
                    if value == 'False':
                        BitArray['L1TrigsApplied'] = 0
                    elif value == 'True':
                        BitArray['L1TrigsApplied'] = 1
                    else:
                        raise TypeError("L1TrigApplied should be a bool type.")

                elif call == 'L1Scaledown':
                    if 0 <= int(value) <= 255:
                        BitArray['L1Scaledown'] = int(value)
                    else:
                        raise KeyError(str(value) + " Value is not within range.")

                elif call == 'L1SingleFreqSuppressRatio':
                    value = round(float(value)*255+0.1)
                    if 26 <= value <= 255:
                        BitArray['L1SingleFreqSuppressRatio'] = value
                    else:
                        raise KeyError(str(value) + " Value is not within range.")

                elif call == 'CommWinConnectTOmins':
                    Time, Comm = value.split(',')
                    if Comm in CommType and 0 <= int(Time) <= 255:
                        BitArray['CommWinConnectTOmins'] = [int(Time), CommType[Comm]]
                    else:
                        raise KeyError(str(value) + " is not a Comm Type.")

                elif call == 'CommWinListenTOmins':
                    Time, Comm = value.split(',')
                    if Comm in CommType and 0 <= int(Time) <= 255:
                        BitArray['CommWinListenTOmins'] = [int(Time), CommType[Comm]]
                    else:
                        raise KeyError(str(value) + " is not a Comm Type.")

                elif call == 'PowerOnFor':
                    if value in PowerMode:
                        BitArray['PowerOnFor'] |= PowerMode[value]
                    else:
                        raise KeyError(str(value) + " is not a Power Mode.")

                elif call == 'WvLoseLSB':
                    if 0 <= int(value) <= 16:
                        BitArray['WvLoseLSB'] = int(value)
                    else:
                        raise KeyError(str(value) + " Value is not within range.")

                elif call == 'WvLoseMSB':
                    if 0 <= int(value) <= 16:
                        BitArray['WvLoseMSB'] = int(value)
                    else:
                        raise KeyError(str(value) + " Value is not within range.")

                elif call == 'WvBaseline':
                    if 0 <= int(value) <= 16:
                        BitArray['WvBaseline'] = int(value)
                    else:
                        raise KeyError(str(value) + " Value is not within range.")

                elif call == 'WatchdogPeriod':
                    if 300 <= int(value) <= 3600:
                        BitArray['WatchdogPeriod'] = int(value)
                    else:
                        raise KeyError(str(value) + " Value is not within range.")
                else:
                    raise KeyError(str(call) + " Call is not listed as an acceptable setting.")

    if len(BitArray) != len(ConfSettings):
        for Sett in ConfSettings:
            if Sett not in BitArray:
                raise KeyError(str(Sett) + " not set in Config.")
    else:
        SaveToDAT(BitArray)

if __name__=="__main__":
    GetConf(sys.argv[0])
