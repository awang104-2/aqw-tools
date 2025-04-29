from handlers.ConfigHandler import SafeDict, get_config
from network.processing import Processor
from network.sniffing import Sniffer
from threading import Thread, Lock
from debug.logger import Logger
from network.layers import Raw
from game import packets


_config = get_config('backend.toml')

SENTINEL = b'STOP INTERPRETING'
AQW_SERVERS = SafeDict(_config['AQW']['SERVERS'])
AQW_PACKETS = SafeDict(_config['AQW']['PACKETS'])
AQW_SERVER_NAMES = list(AQW_SERVERS.keys())
AQW_SERVER_IPS = list(AQW_SERVERS.values())


class GameSniffer(Sniffer):

    def __init__(self, server, stop_filter, *, daemon=False, log=None):
        server_filter = ''
        if server == 'any' or server == 'all':
            for ip in AQW_SERVER_IPS:
                server_filter += f'src host {ip} or '
            server_filter = server_filter[:-4]
        elif server in AQW_SERVER_NAMES or server in AQW_SERVER_IPS:
            server = AQW_SERVERS.get(server, server).lower()
            server_filter = f'src host {server}'
        else:
            raise ValueError('Not a valid server.')
        bpf_filter = f'tcp and ({server_filter})'
        super().__init__(bpf_filter=bpf_filter, stop_filter=stop_filter, layers=[Raw], daemon=daemon, log=log)
        self.server = server


class Updater:

    def __init__(self, character, server, *, daemon=False, log=None):
        self.character = character
        self.sniffer = GameSniffer(server=server, stop_filter='dummy', daemon=True, log=log)
        self.processor = Processor(self.sniffer, daemon=True, log=log)
        self._interpreter = Thread(target=self.interpret, name='Interpreting Thread', daemon=daemon)
        self._lock = Lock()
        self.logger = Logger(log, 'character updater')
        self.logger.clear()

    @property
    def daemon(self):
        with self._lock:
            return self._interpreter.daemon

    @daemon.setter
    def daemon(self, daemon):
        with self._lock:
            self._interpreter.daemon = daemon

    @property
    def running(self):
        with self._lock:
            return self._interpreter.is_alive()

    def connect(self):
        with self._lock:
            self.logger.info('Attempting to connect Updater.')
            self.sniffer.start()
            self.processor.start()
            self.logger.info('Updater connected.')

    def disconnect(self, timeout=None):
        with self._lock:
            self.logger.info('Attempting to disconnect Updater.')
            self.processor.stop(timeout)
            self.sniffer.stop(timeout)
            self.logger.info('Updater disconnected.')

    def force_quit(self):
        with self._lock:
            try:
                self.sniffer.force_quit()
                self.processor.force_quit()
            except RuntimeError as e:
                self.logger.error('Interpreter forced shutdown failed.')
                raise e

    def start(self):
        if not self.running:
            with self._lock:
                self._interpreter.start()

    def stop(self, timeout=None):
        if self.running:
            with self._lock:
                self.processor.jsons.put(SENTINEL)
                self._interpreter.join(timeout)

    def reset(self):
        self.logger.info('Attempting Updater reset.')
        if not self.running:
            with self._lock:
                daemon = self._interpreter.daemon
                self._interpreter = Thread(target=self.interpret, name='Interpreting Thread', daemon=daemon)
                self.logger.info('Updater reset was successful.')
        else:
            self.logger.error('Updater reset failed: Updater was still running.')

    def reset_connection(self):
        if not self.connected('any'):
            self.sniffer.reset()
            self.processor.reset()

    def connected(self, process: str):
        with self._lock:
            match process:
                case 'sniffer':
                    return self.sniffer.running
                case 'processor':
                    return self.processor.running
                case 'any':
                    return self.sniffer.running or self.processor.running
                case 'all':
                    return self.sniffer.running and self.processor.running
            raise ValueError('Argument must be \'sniffer\', \'processor\', \'any\', or \'all\'.')

    def interpret(self):
        while True:
            json = self.processor.jsons.get()
            if json == SENTINEL:
                break
            if json:
                try:
                    json = json['b']['o']
                except KeyError as e:
                    self.logger.error(f'Key Error: {json}')
                    self.logger.error(f'{e}')
                packets.update_character(json, self.character, self.logger)

