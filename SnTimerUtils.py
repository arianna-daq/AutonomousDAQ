import time

class Stopwatch:

    def __init__(self):
        self._start = time.perf_counter()
        self._end = None

    def duration(self):
        return self._end - self._start if self._end else time.perf_counter() - self._start

    def running(self):
        return not self._end

    def restart(self):
        self._start = time.perf_counter()
        self._end = None

    def reset(self):
        self._start = time.perf_counter()
        self._end = self._start

    def start(self):
        if not self.running:
            self._start = time.perf_counter() - self.duration
            self._end = None

    def stop(self):
        if self.running:
            self._end = time.perf_counter()