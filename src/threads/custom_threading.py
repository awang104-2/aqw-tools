from threading import Event, Timer, Thread, RLock
from time import sleep, time
from functools import wraps


def _do_nothing():
    pass


def _with_lock(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


def _check_running(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._running.is_set():
            raise RuntimeError(f'Cannot call \'{method.__name__}\' while {self.__class__.__name__} instance is running.')
        return method(self, *args, **kwargs)
    return wrapper


def _check_not_running(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._running.is_clear():
            raise RuntimeError(f'Cannot call \'{method.__name__}\' while {self.__class__.__name__} instance is not running.')
        return method(self, *args, **kwargs)
    return wrapper


class CustomThread:

    @staticmethod
    def _check_loop(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.loop.is_set() and self.running.is_set() != self.__loop_flag.is_set():
                return _do_nothing()
            else:
                return method(self, *args, **kwargs)
        return wrapper

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None, loop=False, delay=None):
        self.group = group
        self.target = target
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.daemon = daemon
        self.loop = CustomEvent(loop)
        self.delay = delay
        self.thread = Thread(group=self.group, target=self._target, name=self.name, args=self.args, kwargs=self.kwargs, daemon=self.daemon)
        self.__loop_flag = CustomEvent(False)
        self.running = CustomEvent(False)

    def is_running(self):
        return self.running.is_set()

    def _target(self, *args, **kwargs):
        self.running.set()
        if self.loop.is_set():
            self._loop_target(*args, **kwargs)
        else:
            self.target(*args, **kwargs)
        self.reset()
        self.running.clear()

    def _loop_target(self, *args, **kwargs):
        self.__loop_flag.set()
        while self.is_running() and self.__loop_flag.is_set():
            self.target(*args, **kwargs)
            if self.delay:
                sleep(self.delay)

    def wait(self, timeout=None, *, for_clear=True):
        if for_clear:
            self.running.wait_for_clear(timeout)
        else:
            self.running.wait(timeout)

    @_check_loop
    @_check_running
    def start(self):
        self.thread.start()

    @_check_loop
    @_check_running
    def run(self):
        self.thread.run()

    @_check_loop
    @_check_not_running
    def stop(self):
        self.__loop_flag.clear()

    @_check_running
    def reset(self):
        self.thread = Thread(group=self.group, target=self._target, name=self.name, args=self.args, kwargs=self.kwargs, daemon=self.daemon)


class CustomTimer:

    def __init__(self, interval=None, function=None, args=None, kwargs=None, *, name=None, daemon=False, speed=1):
        self._lock = RLock()
        self._parallel = CustomEvent(False)
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
        if self.is_running():
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

    def is_running(self):
        return self._running.is_set()

    def _function(self, *args, **kwargs):
        self.__function(*args, **kwargs)
        self._running.clear()
        self.reset()

    @_check_running
    def start(self):
        self._parallel.set()
        self._start_time = time()
        self._running.set()
        self._timer.start()

    @_check_running
    def run(self):
        self._parallel.clear()
        self._start_time = time()
        self._running.set()
        self._timer.run()

    @_check_not_running
    def cancel(self):
        self._timer.cancel()
        self._running.clear()

    @_check_running
    def reset(self):
        self._start_time = None
        name, daemon = self.name, self.daemon
        self._timer = Timer(interval=self._interval / self._speed, function=self._function, args=self.args, kwargs=self.kwargs)
        self._timer.name = name
        self._timer.daemon = daemon


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

