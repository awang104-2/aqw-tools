from threading import Thread
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
        self.daemon = daemon
        self.character = character
        self.sniffer = GameSniffer(server=server, daemon=True)
        self.interpreter_thread = Thread(target=self.interpret, name='Interpreting JSONs', daemon=self.daemon)

    def force_quit(self):
        self.sniffer.jsons.put(SENTINEL)
        self.interpreter_thread.join()
        self.sniffer.force_quit()

    def start(self):
        self.sniffer.start()
        self.interpreter_thread.start()

    def stop(self, timeout=None):
        self.sniffer.jsons.put(SENTINEL)
        self.interpreter_thread.join()
        self.sniffer.stop()

    def reset(self):
        self.sniffer = GameSniffer(server=self.sniffer.server, daemon=True)
        self.interpreter_thread = Thread(target=self.interpret, name='Interpreting JSONs', daemon=self.daemon)

    def interpret(self):
        while True:
            json = self.sniffer.get_json(no_wait=False)
            if json == SENTINEL:
                return
            elif json:
                update_character(json, self.character)

