from collections.abc import MutableMapping, MutableSequence, MutableSet
import inspect
import copy
import toml
import os


def get_config(config_name):
    frame = inspect.stack()[1]  # 0 is this function, 1 is the caller
    caller_file = frame.filename
    caller_file = os.path.abspath(caller_file)
    config_path = os.path.join(os.path.dirname(caller_file), 'config', config_name)
    config = toml.load(config_path)
    return config


class Constant(dict):

    def __init__(self, dictionary):
        super().__init__(dictionary)

    def __getitem__(self, key):
        value = super().__getitem__(key)
        if isinstance(value, (MutableMapping, MutableSequence, MutableSet)):
            return copy.deepcopy(value)

    def get(self, key, default=None):
        value = super().get(key, default)
        if isinstance(value, (MutableMapping, MutableSequence, MutableSet)):
            return copy.deepcopy(value)
        return value


__all__ = ['get_config', 'Constant']