import threading
import time


def check_running(method):
    def wrapper(self, *args, **kwargs):
        if self.is_running():
            raise RuntimeError('Cannot use while Interpreter instance is running.')
        return method(self, *args, **kwargs)
    return wrapper


class Interpreter:

    def __init__(self, player, logger, delay=None):
        self.logger = logger
        self.player = player
        self.__running = threading.Event()
        self.__interpret_thread = None
        self.delay = delay

    @check_running
    def set_delay(self, delay):
        self.delay = delay

    @check_running
    def clear_delay(self):
        self.delay = None

    def __add_item(self, added_items):
        for item in added_items:
            item_id = list(item.get('items').keys())[0]
            name = item.get('items').get(item_id).get('sName')
            iQty = item.get('items').get(item_id).get('iQty')

    def __add_drops(self, drops):
        for drop in drops:
            item_id = list(drop.get('items').keys())[0]
            name = drop.get('items').get(item_id).get('sName')
            iQty = drop.get('items').get(item_id).get('iQty')

    def interpret(self):
        sorted_jsons = self.logger.get_sorted_jsons()
        added_items, drops, kills = sorted_jsons.get('addItems', []), sorted_jsons.get('dropItem',[]), sorted_jsons.get('addGoldExp',[])



        if not any(cmd in list(sorted_jsons.keys()) for cmd in commands):
            return
        for data in dataset:
            cmd = data.get('cmd')
            match cmd:
                case 'addItems' | 'dropItem':
                    item_id = list(data.get('items').keys())[0]
                    name = data.get('items').get(item_id).get('sName')
                    iQty = data.get('items').get(item_id).get('iQty')
                    is_drop = cmd == 'dropItem'
                    turn_in_list = self.player.add_drop(item_id, name, iQty, is_drop)
                    if not is_drop:
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
        self.__interpret_thread = threading.Thread(target=self.run, daemon=True, name='interpreter thread')
        self.__interpret_thread.start()

    def stop(self):
        self.__running.clear()
