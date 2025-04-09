from handlers.ConfigHandler import *


_config = get_config('backend.toml')

AQW_SERVERS = SafeDict(_config['AQW']['SERVERS'])
AQW_PACKETS = SafeDict(_config['AQW']['PACKETS'])
AQW_SERVER_NAMES = list(AQW_SERVERS.keys())
AQW_SERVER_IPS = list(AQW_SERVERS.values())


__all__ = [name for name in globals() if not name.startswith('_')]