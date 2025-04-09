from collections.abc import MutableMapping, MutableSequence, MutableSet
import inspect
import copy
import toml
import os


def get_config_path(config_name):
    frame = inspect.stack()[1]  # 0 is this function, 1 is the caller
    caller_file = frame.filename
    caller_file = os.path.abspath(caller_file)
    config_path = os.path.join(os.path.dirname(caller_file), 'config', config_name)
    return config_path


def get_config(config_name):
    frame = inspect.stack()[1]  # 0 is this function, 1 is the caller
    caller_file = frame.filename
    caller_file = os.path.abspath(caller_file)
    config_path = os.path.join(os.path.dirname(caller_file), 'config', config_name)
    config = toml.load(config_path)
    return config


def write_to_file(new_config: dict, filepath):
    try:
        new_config = dict(new_config)
    except TypeError as e:
        raise e
    with open(filepath, 'w') as file:
        toml.dump(new_config, file)


def write_to_config(new_config, config_name):
    try:
        new_config = dict(new_config)
    except TypeError as e:
        raise e
    frame = inspect.stack()[1]  # 0 is this function, 1 is the caller
    caller_file = frame.filename
    caller_file = os.path.abspath(caller_file)
    config_path = os.path.join(os.path.dirname(caller_file), 'config', config_name)
    write_to_file(new_config, config_path)


class SafeDict(MutableMapping):

    def __init__(self, dictionary):
        self._dictionary = dictionary

    def __setitem__(self, key, value, /):
        self._dictionary[key] = value

    def __delitem__(self, key, /):
        del self._dictionary[key]

    def __len__(self):
        return len(self._dictionary)

    def __iter__(self):
        return iter(self._dictionary)

    def __getitem__(self, key):
        value = self._dictionary[key]
        if isinstance(value, (MutableMapping, MutableSequence, MutableSet)):
            return copy.deepcopy(value)
        return value

    def get(self, key, default=None):
        value = self._dictionary.get(key, default)
        if isinstance(value, (MutableMapping, MutableSequence, MutableSet)):
            return copy.deepcopy(value)
        return value

    def values(self):
        dictionary = {}
        for i, value in enumerate(self._dictionary.values()):
            if isinstance(value, (MutableMapping, MutableSequence, MutableSet)):
                value = copy.deepcopy(value)
            dictionary[i] = value
        return dictionary.values()

    def keys(self):
        return self._dictionary.keys()

    def items(self):
        dictionary = {}
        for key, value in self._dictionary.items():
            if isinstance(value, (MutableMapping, MutableSequence, MutableSet)):
                value = copy.deepcopy(value)
            dictionary[key] = value
        return dictionary.items()

    def update(self, other=(), /, **kwargs):
        self._dictionary.update(other, **kwargs)

    def __dict__(self):
        return self._dictionary

    def __str__(self):
        return str(self._dictionary)

    def __repr__(self):
        return f'SafeDict({self._dictionary})'


__all__ = [name for name in globals() if not name.startswith('-')]