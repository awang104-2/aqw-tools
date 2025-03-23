from threading import Event, Timer, Thread, Lock, RLock
from time import sleep, time
from functools import wraps


def do_nothing():
    pass


def with_lock(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


def check_running(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.running.is_set():
            class_name = self.__class__.__name__
            method_name = method.__name__
            raise RuntimeError(f'Cannot run \'{class_name}.{method_name}\' while thread is running.')
        return method(self, *args, **kwargs)
    return wrapper


def check_not_running(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.running.is_clear():
            class_name = self.__class__.__name__
            method_name = method.__name__
            raise RuntimeError(f'Cannot run \'{class_name}.{method_name}\' while thread is not running.')
        return method(self, *args, **kwargs)
    return wrapper


class CustomThread:

    @staticmethod
    def check_loop(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.loop.is_set() and self.running.is_set() != self.__loop_flag.is_set():
                return do_nothing()
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

    @check_running
    @check_loop
    def start(self):
        self.thread.start()

    @check_running
    @check_loop
    def run(self):
        self.thread.run()

    @check_not_running
    @check_loop
    def stop(self):
        self.__loop_flag.clear()

    def wait(self, timeout=None, *, for_clear=True):
        if for_clear:
            self.running.wait_for_clear(timeout)
        else:
            self.running.wait(timeout)

    def reset(self):
        self.thread = Thread(group=self.group, target=self._target, name=self.name, args=self.args, kwargs=self.kwargs, daemon=self.daemon)


class CustomTimer:

    def __init__(self, interval=None, function=None, args=None, kwargs=None, *, name=None, daemon=None, speed=1):
        self._lock = RLock()
        self._parallel = CustomEvent(False)
        self._start_time = None
        self._speed = speed
        self.running = CustomEvent(False)
        self._interval = interval
        self.function = function
        self.daemon = daemon
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.timer = Timer(interval=self._interval / self._speed, function=self._function, args=self.args, kwargs=self.kwargs)

    @property
    def elapsed(self):
        with self._lock:
            if self._start_time is None:
                return 0
            return min(time() - self._start_time, self._interval)

    @property
    def interval(self):
        with self._lock:
            if self._start_time is None:
                return self._interval
            print(min(time() - self._start_time, self._interval))
            print(self._interval)
            return self._interval - min(time() - self._start_time, self._interval)

    @interval.setter
    def interval(self, new_time):
        with self._lock:
            if new_time < 0:
                raise ValueError('Interval must be non-negative.')
            self._interval = new_time
            print(self.is_running())
            if self.is_running():
                print(self._parallel.is_clear())
                if self._parallel.is_clear():
                    raise RuntimeError('Cannot adjust speed while running in blocking mode (.run()).')
                self.cancel()
                self.reset()
                self.start()

    @property
    def speed(self):
        with self._lock:
            return self._speed

    @speed.setter
    def speed(self, new_speed):
        with self._lock:
            self._speed = new_speed
            if self.is_running():
                if self._parallel.is_clear():
                    raise RuntimeError('Cannot adjust speed while running in blocking mode (.run()).')
                self._interval = self.interval
                self.cancel()
                self.reset()
                self.start()

    @with_lock
    def join(self):
        self.timer.join()
        self._parallel.clear()

    def is_running(self):
        return self.running.is_set()

    def _function(self, *args, **kwargs):
        self.function(*args, **kwargs)
        self.running.clear()
        self._reset()

    @check_running
    def start(self):
        self._parallel.set()
        self._start_time = time()
        self.running.set()
        self.timer.start()

    @check_running
    def run(self):
        self._parallel.clear()
        self._start_time = time()
        self.running.set()
        self.timer.run()

    @with_lock
    @check_not_running
    def cancel(self):
        self.timer.cancel()
        self.running.clear()

    @with_lock
    @check_running
    def reset(self):
        self._reset()

    def _reset(self):
        self._start_time = None
        self.timer = Timer(self._interval / self._speed, self._function, self.args, self.kwargs)
        if self.name:
            self.timer.name = self.name
        self.timer.daemon = self.daemon


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

