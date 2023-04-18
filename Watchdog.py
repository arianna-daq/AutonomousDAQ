from threading import Timer
import os
from SnConstants import *

class Watchdog:
    WDPeriod  = None
    PrevReset = None

    def Starter(self, WD_period):
        Watchdog().WDPeriod = WD_period

        temp = open("WD.dat", 'r+')
        Watchdog().PrevReset = temp.read(1)
        temp.seek(0)
        temp.write("0")
        temp.close()

        self.WD_timer = Timer(Watchdog().WDPeriod, self.RESET)
        self.WD_timer.start()        

    def RESET(self):
        temp = open("WD.dat", 'w')
        temp.write("1")
        temp.close()

        os.system('sudo reboot')

    def kick(self, *args):
        if args:
            Watchdog().WDPeriod = args[0]
            self.WD_timer.cancel()
            self.WD_timer = Timer(Watchdog().WDPeriod, self.RESET)
        else:
            self.WD_timer.cancel()
            self.WD_timer = Timer(Watchdog().WDPeriod, self.RESET)

    def didWatchdogReset(self):
        return int(Watchdog().PrevReset)
    
    def values(self):
        return Watchdog().WDPeriod

        
if __name__=="__main__":
    Watchdog().Starter(WDFAILSAFE)
    print(Watchdog())

