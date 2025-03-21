from threads.custom_threading import CustomEvent, CustomThread
import time


def check_running(method):
    def wrapper(self, *args, **kwargs):
        if self.is_running():
            raise RuntimeError(f'Cannot call \'{method.__name__}\' while Interpreter instance is running.')
        return method(self, *args, **kwargs)
    return wrapper


class Interpreter:

    def __init__(self, player, logger, delay=None):
        self.logger = logger
        self.player = player
        self.__interpret_thread = CustomThread(target=self.__interpret_packets_loop, daemon=True, name='interpreter thread')
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
            self.player.add_item(item_id=item_id, name=name, iQty=iQty)
            iQtyNow = item.get('items').get(item_id).get('iQtyNow', None)
            if iQtyNow:
                self.player.set_inventory(item_id, iQtyNow)

    def __add_drops(self, drops):
        for drop in drops:
            item_id = list(drop.get('items').keys())[0]
            name = drop.get('items').get(item_id).get('sName')
            iQty = drop.get('items').get(item_id).get('iQty')
            self.player.add_drop(item_id=item_id, name=name, iQty=iQty)

    def __add_kills(self, kills):
        for kill in kills:
            kill.get('id')
            self.player.kill()

    def interpret(self):
        sorted_jsons = self.logger.get_sorted_jsons()
        added_items, drops, kills = sorted_jsons.get('addItems', []), sorted_jsons.get('dropItem',[]), sorted_jsons.get('addGoldExpM',[])
        self.__add_item(added_items)
        self.__add_drops(drops)
        self.__add_kills(kills)

    def __interpret_packets_loop(self):
        while self.logger.is_running() and self.is_running():
            if not self.delay:
                self.logger.wait_for_packet()
                self.interpret()
            else:
                self.interpret()
                time.sleep(self.delay)

    def is_running(self):
        return self.__interpret_thread.is_running()

    @check_running
    def run(self):
        self.__interpret_thread.run()

    @check_running
    def start(self):
        self.__interpret_thread.start()

    def stop(self):
        self.__interpret_thread.stop()
