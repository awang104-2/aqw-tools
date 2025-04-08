from functools import wraps


def with_lock(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._buffer_lock:
            return method(self, *args, **kwargs)
    return wrapper


def check_repeating(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self._loopable.is_clear():
            raise RuntimeError(f'Cannot call \'{method.__name__}\' if {self.__class__.__name__}.loop is False.')
        return method(self, *args, **kwargs)
    return wrapper


def with_packets_lock(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._packets_lock:
            return method(self, *args, **kwargs)
    return wrapper


def check_running(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.running:
            raise RuntimeError(f'Cannot call \'{method.__name__}\' while {self.__class__.__name__} instance is not running.')
        return method(self, *args, **kwargs)
    return wrapper


def check_not_running(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.running:
            raise RuntimeError(f'Cannot call \'{method.__name__}\' while {self.__class__.__name__} instance is running.')
        return method(self, *args, **kwargs)
    return wrapper


def needs_character_initialized(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.character:
            raise RuntimeError(f'Character must be initialized before calling \'{self.__class__.__name__}.{method.__name__}\'.')
        return method(self, *args, **kwargs)
    return wrapper


__all__ = [name for name in globals() if not name.startswith('-')]
