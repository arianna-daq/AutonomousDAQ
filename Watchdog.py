from threading import Timer
import os

class Watchdog:
    def Starter(self, WD_period):
        self.period = WD_period

        temp = open("WD.dat", 'r+')
        self.Prev_reset = temp.read(1)
        temp.seek(0)
        temp.write("0")
        temp.close()

        self.WD_timer = Timer(self.period, self.RESET)
        self.WD_timer.start()        

    def RESET(self):
        temp = open("WD.dat", 'w')
        temp.write("1")
        temp.close()

        os.system('sudo reboot')

    def kick(self):
        self.WD_timer.cancel()
        self.WD_timer = Timer(self.period, self.RESET)

    def didWatchdogReset(self):
        return int(self.Prev_reset)

        


