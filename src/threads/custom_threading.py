from threading import Event, Timer, Thread, RLock
from decorators._decorators import *
from time import sleep, time


class LoopingThread:

    def __init__(self, *, target=None, flag=None, name=None, args=(), kwargs=None, daemon=None):
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self._thread = Thread(target=self._looped_target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        if flag:
            self._loop_flag = flag
        else:
            self._loop_flag = Event()

    @property
    def name(self):
        return self._thread.name

    @property
    def daemon(self):
        return self._thread.daemon

    @property
    def running(self):
        return self._thread.is_alive()

    @property
    def ready(self):
        return not self._thread.is_alive()

    def _looped_target(self, *args, **kwargs):
        self._loop_flag.set()
        while self._loop_flag.is_set():
            self.target(*args, **kwargs)

    @check_not_running
    def start(self):
        self._thread.start()

    @check_not_running
    def run(self):
        self._thread.run()

    @check_repeating
    @check_running
    def stop(self):
        self._loop_flag.clear()

    @check_not_running
    def reset(self):
        self._thread = Thread(target=self._looped_target, name=self.name, args=self.args, kwargs=self.kwargs, daemon=self.daemon)

    @check_running
    def join(self, timeout=None):
        self._thread.join(timeout=timeout)


class AdjustableTimer:

    def __init__(self, interval=None, function=None, args=None, kwargs=None, *, name=None, daemon=False, speed=1):
        self._lock = RLock()
        self._parallel = Event()
        self._running = CustomEvent(False)
        self._start_time = None
        self._speed = speed
        self._interval = interval
        self.__function = function
        self._timer = Timer(interval=self._interval / self._speed, function=self._function, args=args, kwargs=kwargs)
        if name:
            self._timer.name = name
        self._timer.daemon = daemon

    @property
    def running(self):
        return self._running.is_set()

    @property
    def ready(self):
        return self._running.is_clear()

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval):
        self._interval = interval

    @property
    def function(self):
        return self.__function

    @function.setter
    def function(self, function):
        self.__function = function

    @property
    def args(self):
        return self._timer.args

    @args.setter
    def args(self, args):
        self._timer.args = args

    @property
    def kwargs(self):
        return self._timer.kwargs

    @kwargs.setter
    def kwargs(self, kwargs):
        self._timer.kwargs = kwargs

    @property
    def name(self):
        return self._timer.name

    @name.setter
    def name(self, name):
        self._timer.name = name

    @property
    def daemon(self):
        return self._timer.daemon

    @daemon.setter
    def daemon(self, daemon):
        self._timer.daemon = daemon

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed

    @property
    def elapsed(self):
        if self._start_time is None:
            return 0
        return min(time() - self._start_time, self._interval)

    @property
    def remaining(self):
        return self._interval - self.elapsed

    def adjust(self, speed):
        self._speed = speed
        if self.running:
            self._timer.cancel()
            name, daemon = self.name, self.daemon
            interval = max(self._interval / self._speed - self.elapsed, 0)
            self._timer = Timer(interval=interval, function=self._function, args=self.args, kwargs=self.kwargs)
            self._timer.name = name
            self._timer.daemon = daemon
            self._timer.start()

    def join(self):
        self._timer.join()
        self._parallel.clear()

    def _function(self, *args, **kwargs):
        if self.__function:
            self.__function(*args, **kwargs)
        self._running.clear()
        self.reset()

    @check_not_running
    def start(self):
        self._parallel.set()
        self._start_time = time()
        self._running.set()
        self._timer.start()

    @check_not_running
    def run(self):
        self._parallel.clear()
        self._start_time = time()
        self._running.set()
        self._timer.run()

    @check_running
    def cancel(self):
        self._timer.cancel()
        self._running.clear()

    @check_not_running
    def reset(self):
        self._start_time = None
        name, daemon = self.name, self.daemon
        self._timer = Timer(interval=self._interval / self._speed, function=self._function, args=self.args, kwargs=self.kwargs)
        self._timer.name = name
        self._timer.daemon = daemon

    def wait_until_ready(self, timeout=None):
        self._running.wait_for_clear(timeout=timeout)


class CustomEvent(Event):

    def __init__(self, is_set=None):
        super().__init__()
        self.opp_event = Event()
        if is_set:
            self.set()
        else:
            self.opp_event.set()

    def set(self):
        self.opp_event.clear()
        super().set()

    def clear(self):
        self.opp_event.set()
        super().clear()

    def is_clear(self):
        return self.opp_event.is_set()

    def wait_for_clear(self, timeout=None):
        self.opp_event.wait(timeout)

    def wait_min(self, minimum):
        sleep(minimum)
        self.wait()

__all__ = ['CustomEvent', 'LoopingThread', 'AdjustableTimer']