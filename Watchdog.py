import os
from threading import Timer

class Watchdog:
    def __init__(self, WD_period):
        self.period = WD_period
        self.WD_timer = Timer(self.period, self.RESET_RPi)

        temp = open("WD.dat", 'r')
        self.Prev_reset = temp.read(1)
        temp.seek(0)
        temp.write("0")
        temp.close()

    def RESET_RPi(self):
        temp = open("WD.dat", 'w')
        temp.write("1")
        temp.close()

        os.system('sudo shutdown -r now')

    def kick(self):
        self.WD_timer.cancel()
        self.WD_timer = Timer(self.period, self.RESET_RPi)

    def didWatchdogReset(self):
        return int(self.Prev_reset)

        


