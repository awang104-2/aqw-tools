from threading import Thread, Lock
from game.packets import GameSniffer, update_character


SENTINEL = b'STOP INTERPRETING'


class UpdaterRunningError(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class UpdaterConnectionError(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class Updater:

    def __init__(self, character, server='any', *, daemon=False):
        self.character = character
        self.sniffer = GameSniffer(server=server, daemon=True)
        self._interpreter = Thread(target=self.interpret, name='Interpreting Thread', daemon=daemon)
        self._lock = Lock()

    @property
    def daemon(self):
        with self._lock:
            return self._interpreter.daemon

    @daemon.setter
    def daemon(self, daemon):
        with self._lock:
            self._interpreter.daemon = daemon

    def is_alive(self):
        with self._lock:
            return self._interpreter.is_alive()

    def connect(self):
        if self.connected():
            raise UpdaterConnectionError('Updater cannot connect if connected.')
        with self._lock:
            self.sniffer.start()
            self.processor.start()

    def disconnect(self, timeout=None):
        if not self.connected('any'):
            raise UpdaterConnectionError('Updater cannot disconnect if not connected.')
        with self._lock:
            self.processor.stop(timeout)
            self.sniffer.stop(timeout)

    def force_quit(self):
        if not self.is_alive:
            raise UpdaterRunningError('Updater cannot force quit while not running.')
        with self._lock:
            self.sniffer.force_quit()
            self.processor.force_quit()

    def start(self):
        if self.is_alive:
            raise UpdaterRunningError('Updater cannot start while running.')
        with self._lock:
            self._interpreter.start()

    def stop(self, timeout=None):
        if not self.is_alive:
            raise UpdaterRunningError('Updater cannot stop while not running.')
        with self._lock:
            self.processor.jsons.put(SENTINEL)
            self._interpreter.join(timeout)

    def reset(self):
        if self.is_alive:
            raise UpdaterRunningError('Updater cannot reset while running.')
        elif self.connected('any'):
            raise UpdaterConnectionError('Updater cannot reset while connected.')
        with self._lock:
            server = self.sniffer.server
            daemon = self._interpreter.daemon
            self.sniffer = GameSniffer(server=server, daemon=True)
            self._interpreter = Thread(target=self.interpret, name='Interpreting Thread', daemon=daemon)

    def connected(self):
        with self._lock:
            return self.sniffer.is_alive()

    def interpret(self):
        while True:
            json = self.sniffer.get_json(no_wait=False)
            if json == SENTINEL:
                break

