from threading import Event, Timer, Thread
from time import sleep
from functools import wraps


def do_nothing():
    pass

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
        self.thread = Thread(group=self.group, target=self.__target, name=self.name, args=self.args, kwargs=self.kwargs, daemon=self.daemon)
        self.__loop_flag = CustomEvent(False)
        self.running = CustomEvent(False)

    def is_running(self):
        return self.running.is_set()

    def __target(self, *args, **kwargs):
        self.running.set()
        if self.loop.is_set():
            self.__loop_target(*args, **kwargs)
        else:
            self.target(*args, **kwargs)
        self.reset()
        self.running.clear()

    def __loop_target(self, *args, **kwargs):
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
        self.thread = Thread(group=self.group, target=self.__target, name=self.name, args=self.args, kwargs=self.kwargs, daemon=self.daemon)


class CustomTimer:

    def __init__(self, interval=None, function=None, args=None, kwargs=None, *, name=None, daemon=None):
        self.running = CustomEvent(False)
        self.interval = interval
        self.function = function
        self.daemon = daemon
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.timer = Timer(interval=self.interval, function=self.__function, args=self.args, kwargs=self.kwargs)

    def is_running(self):
        return self.running.is_set()

    def __function(self, *args, **kwargs):
        self.running.set()
        self.function(*args, **kwargs)
        self.reset()
        self.running.clear()

    @check_running
    def start(self):
        self.timer.start()

    @check_running
    def run(self):
        self.timer.run()

    @check_not_running
    def cancel(self):
        self.timer.cancel()
        self.running.clear()

    def reset(self):
        self.timer = Timer(self.interval, self.__function)
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
