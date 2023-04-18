from threading import Timer
import os
from SnConstants import *

class Watchdog:
    def __init__(self, WD_period):
        self.WDPeriod = WD_period

        temp = open("WD.dat", 'r+')
        self.PrevReset = temp.read(1)
        temp.seek(0)
        temp.write("0")
        temp.close()

        self.WD_timer = Timer(self.WDPeriod, self.RESET)
        self.WD_timer.start()        

    def RESET(self):
        temp = open("WD.dat", 'w')
        temp.write("1")
        temp.close()

        os.system('sudo reboot')

    def kick(self, *args):
        if args:
            self.WDPeriod = args[0]
            self.WD_timer.cancel()
            self.WD_timer = Timer(self.WDPeriod, self.RESET)
            self.WD_timer.start()
        else:
            self.WD_timer.cancel()
            self.WD_timer = Timer(self.WDPeriod, self.RESET)
            self.WD_timer.start()

    def didWatchdogReset(self):
        return int(self.PrevReset)
    
    def __str__(self):
        return "%s" % (self.WDPeriod)

        
if __name__=="__main__":
    Watchdog().Starter(WDFAILSAFE)
    print(Watchdog())

