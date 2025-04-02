from handlers.DictHandler import deepcopy
import toml
import os


_backend_path = os.path.join(os.path.dirname(__file__), 'config', 'backend.toml')
with open(_backend_path, 'r') as file:
    _backend = toml.load(file)

AQW_SERVERS = deepcopy(_backend['AQW']['SERVERS'])
AQW_PACKETS = deepcopy(_backend['AQW']['PACKETS'])
AQW_SERVER_NAMES = list(AQW_SERVERS.keys())
AQW_SERVER_IPS = list(AQW_SERVERS.values())


__all__ = [name for name in globals() if not name.startswith('_')]