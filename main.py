#python main.py

import numpy as np
import smbus
import SnConstants as C
import SnConfigFrame as Conf

bus = smbus.SMBus(1)

def SetSstDACs():
    """Sends the High and Low thresholds to the LTC2657 DAC Chip via I2C"""

    dadr, dv, dn = 0, 0, 0
    LSB, MSB = 0, 0

    for ch in range(C.Nchans):
        dadr = C.LTC2657Addr[int(ch / C.ChansPerLTC2657)]
        
        for dc in range(C.NchanDacs):
            dok = False 
            
            for tries in range(C.MaxDacSetTries):
                if dok == True:
                    break
                
                dn = (C.ChansPerLTC2657*C.NchanDacs) - (dc*C.ChansPerLTC2657) - C.ChansPerLTC2657 + (ch % C.ChansPerLTC2657)
                
                if dn > 7:
                    print("TotDacs=%d, dc=%d, ch=%d, ChansPerLTC2657=%d, dn=%d\n" % (C.TotDacs, dc, ch, C.ChansPerLTC2657, dn))
                    raise("chan/dac combination too big for 3 bits!")

                dn |= (C.UpdateDacCmd << 4)
                dv = Conf.GetDac(ch, dc)
                MSB = (dv & 65280) >> 8
                LSB = (dv & 255)
                bus.write_i2c_block_data(dadr, dn, [int(MSB), int(LSB)])
                dok = True

if __name__=="__main__":
    SetSstDACs()