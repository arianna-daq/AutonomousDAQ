from threading import Timer
from SnConstants import *

class SnTickerTimer:
    def __init__(self, period, func):

        if period > kAbsMaxTimer:
            self.period = kAbsMaxTimer
        else:
            self.period = period

        self.func = func
        self.Timer = Timer(self.period, self.func)

        if self.period > 0:    
            self.Timer.start()

    def RESTART(self, *args):
        if args: 
            if args[0] > kAbsMaxTimer:
                self.period = kAbsMaxTimer
            else:
                self.period = args[0]
                
            self.Timer.cancel()
            self.Timer = Timer(self.period, self.func)
        else:
            self.Timer.cancel()
            self.Timer = Timer(self.period, self.func)

        if self.period > 0:    
            self.Timer.start()
    
    def STOP(self):
        self.Timer.cancel()
        self.Timer = Timer(self.period, self.func)

    def __str__(self):
        return "%s" % (self.period)
