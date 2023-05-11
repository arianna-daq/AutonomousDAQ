from threading import Timer
from SnConstants import *

class TickerTimer:
    def __init__(self, period, func):
        self.period = period
        self.func = func

        self.Timer = Timer(self.period, self.func)
        self.Timer.start()

    def RESET(self):
        self.Timer.cancel()
        self.Timer = Timer(self.period, self.func)
        self.Timer.start()

    def __str__(self):
        return "%s" % (self.period)
