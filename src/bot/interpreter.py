import threading
import time


class Interpreter:

    def __init__(self, player, logger, delay=None):
        self.logger = logger
        self.player = player
        self.__running = threading.Event()
        self.__interpret_thread = None
        self.delay = delay

    def set_delay(self, delay):
        if not self.is_running():
            self.delay = delay

    def clear_delay(self):
        if not self.is_running():
            self.delay = None

    def interpret(self):
        dataset = self.logger.get_jsons()
        for data in dataset:
            cmd = data.get('cmd')
            match cmd:
                case 'addItems' | 'dropItem':
                    item_id = list(data.get('items').keys())[0]
                    name = data.get('items').get(item_id).get('sName')
                    iQty = data.get('items').get(item_id).get('iQty')
                    self.player.add_drop(item_id, name, iQty, cmd == 'dropItem')
                    if cmd == 'addItems':
                        iQtyNow = data.get('items').get(item_id).get('iQtyNow', None)
                        if iQtyNow:
                            self.player.set_inventory(item_id, iQtyNow)
                case 'addGoldExp':
                    if data.get('id'):
                        self.player.kill()

    def __interpret_packets_loop(self):
        while self.logger.is_running() and self.is_running():
            if not self.delay:
                self.logger.wait_for_packet()
                self.interpret()
            else:
                self.interpret()
                time.sleep(self.delay)

    def is_running(self):
        return self.__running.is_set()

    def run(self):
        self.__running.set()
        self.__interpret_packets_loop()
        self.__running.clear()

    def start(self):
        self.__interpret_thread = threading.Thread(target=self.run, daemon=True)
        self.__interpret_thread.name = 'interpreter thread'
        self.__interpret_thread.start()

    def stop(self):
        self.__running.clear()