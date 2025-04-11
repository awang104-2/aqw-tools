from threading import Event, RLock


def _initialize(my_class):
    kwargs = {}
    for name, value in vars(my_class).items():
        if not name.startswith('_') and not callable(value):
            kwargs[value] = Event()
    return kwargs


def access_class_variables(my_class):
    kwargs = {}
    for name, value in vars(my_class).items():
        if not name.startswith('_') and not callable(value):
            kwargs[name] = value
    return kwargs


def load(boss_name, *, args: tuple | list = (), kwargs: dict | None = None):
    if kwargs is None:
        kwargs = {}
    cls = globals().get(boss_name)
    if cls:
        return cls(*args, **kwargs)
    else:
        raise ValueError(f'Invalid boss name \'{boss_name}\', use boss names {BOSS_NAMES}.')


class Boss:

    def __init__(self):
        self._events = {}
        self._lock = RLock()

    def trigger(self, event_key):
        with self._lock:
            self._events[event_key].set()

    def resolve(self, event_key):
        with self._lock:
            self._events[event_key].clear()

    def get(self, event_key):
        with self._lock:
            return self._events[event_key].is_set()


class Bosses:

    def __init__(self, *args):
        self._lock = RLock()
        self._bosses = {}
        for arg in args:
            self._bosses[arg] = load(arg)

    def __getitem__(self, key):
        with self._lock:
            return self._bosses[key]

    def __setitem__(self, key, value):
        with self._lock:
            self._bosses[key] = value

    def bosses(self):
        with self._lock:
            return list(self._bosses.values())

    def names(self):
        with self._lock:
            return list(self._bosses.keys())

    def reinitialize(self, *bosses):
        with self._lock:
            self._bosses = {}
            for boss in bosses:
                self._bosses[boss] = load(boss)


class Malgor(Boss):

    TRUTH = 'I will make you see the truth.'
    LISTEN = 'You shall listen.'
    RED = 'All stand equal beneath the eyes of the Eternal.'

    def __init__(self):
        super().__init__()
        self._events.update(_initialize(type(self)))

    def trigger(self, msg):
        super().trigger(msg)

class Drakath(Boss):

    HP_CHECKPOINTS = [x * 2000000 for x in range(10) if not x in (0, 5)]
    TOLERANCE = 0.1

    def __init__(self):
        super().__init__()
        for checkpoint in Drakath.HP_CHECKPOINTS:
            self._events[checkpoint] = Event()
        self._tolerance = Drakath.TOLERANCE
        self._hp = 20000000

    @property
    def tolerance(self):
        with self._lock:
            return self._tolerance

    @tolerance.setter
    def tolerance(self, tolerance):
        with self._lock:
            self._tolerance = tolerance

    @property
    def health(self):
        with self._lock:
            return self._hp

    @health.setter
    def health(self, hp):
        self._hp = hp

    def trigger(self, hp):
        with self._lock:
            if (self._hp - hp) / Drakath.HP_CHECKPOINT < self._tolerance and (hp % Drakath.HP_CHECKPOINT) / Drakath.HP_CHECKPOINT < self._tolerance:
                super().trigger(Drakath.HP_CHECKPOINT)
                self._hp = hp

    def resolve(self, hp=None):
        super().resolve(Drakath.HP_CHECKPOINT)




BOSS_NAMES = [k for k, v in globals().items() if isinstance(v, type) and issubclass(v, Boss) and v is not Boss]

__all__ = [x for x in globals() if not x.startswith('_')]




