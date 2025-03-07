from threading import Event, Timer


class EditableTimer(Timer):

    def add_time(self, time):
        self.interval += time

    def subtract_time(self, time):
        if time >= self.interval:
            self.interval = 0
        else:
            self.interval -= time


class CustomTimer:

    def __init__(self, interval=None, function=None, daemon=False, move=None, name=None):
        self.interval = interval
        self.function = function
        self.daemon = daemon
        self.timer = EditableTimer(self.interval, self.__function)
        self.name = name
        if self.name:
            self.timer.name = name
        self.timer.daemon = self.daemon
        self.move = move

    def add_time(self, time, condition=None):
        if not condition:
            self.timer.add_time(time)

    def set_parameters(self, interval=None, function=None, daemon=None, move=None, name=None):
        if interval:
            self.interval = interval
        if function:
            self.function = function
        if daemon:
            self.daemon = daemon
        if move:
            self.move = move
        if name:
            self.name = name
        self.reset()

    def __function(self, *args):
        self.function()
        self.reset()

    def start(self):
        self.timer.start()

    def run(self):
        self.timer.run()

    def cancel(self):
        self.timer.cancel()

    def reset(self):
        self.timer = EditableTimer(self.interval, self.__function)
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