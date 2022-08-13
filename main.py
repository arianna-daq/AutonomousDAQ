#python main.py

import numpy as np
import smbus
import SnConstants as C
import SnConfigFrame as Conf

bus = smbus.SMBus(1)

def SetSstDACs():
    """Sends the High and Low Thresholds to the LTC2657 DAC Chip via I2C"""

    # Init Variables
    dadr, dv, dn = 0, 0, 0
    LSB, MSB = 0, 0

    for ch in range(C.Nchans):
        dadr = C.LTC2657Addr[int(ch / C.ChansPerLTC2657)]
        
        for dc in range(C.NchanDacs):
            dok = False 
            
            for tries in range(C.MaxDacSetTries):
                if dok == True:
                    break


                # Address for Each DAC Register
                dn = (C.ChansPerLTC2657*C.NchanDacs) - (dc*C.ChansPerLTC2657) - C.ChansPerLTC2657 + (ch % C.ChansPerLTC2657)

                # Raise Error for Invalid Code for LTC2657 DAC Chip
                if dn > 7:
                    print("TotDacs=%d, dc=%d, ch=%d, ChansPerLTC2657=%d, dn=%d\n" % (C.TotDacs, dc, ch, C.ChansPerLTC2657, dn))
                    raise("chan/dac combination too big for 3 bits!")

                # Build Data Bitstream to Send to LTC2657 DAC Chip
                dn |= (C.UpdateDacCmd << 4)
                dv = Conf.GetDac(ch, dc)
                MSB = (dv & 65280) >> 8
                LSB = (dv & 255)

                # Send Data Bitstream to DAC Chip via I2C
                try:
                    bus.write_i2c_block_data(dadr, dn, [int(MSB), int(LSB)])
                    dok = True
                except OSError:
                    dok = False

                print(ch, dc, tries, dok)

if __name__=="__main__":
    SetSstDACs()