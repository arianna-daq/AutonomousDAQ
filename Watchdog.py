import os
from threading import Timer

class Watchdog:
    def __init__(self, WD_period):
        self.period = WD_period
        self.WD_timer = Timer(self.period, self.RESET_RPi)

    def RESET_RPi(self):
        os.system('sudo shutdown -r now')


    def kick(self):
        self.WD_timer.cancel()
        self.WD_timer = Timer(self.period, self.RESET_RPi)

        


