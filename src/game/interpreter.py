from network.processing import Processor
from threading import Thread, Lock
from game.aqw_backend import *
from decorators import *


class JsonDict:

    def __init__(self, dictionary=None):
        self._lock = Lock()
        if dictionary:
            self._jsons = dictionary
        else:
            self._jsons = dict.fromkeys(list(AQW_PACKETS.keys()), [])

    @with_lock
    def __str__(self):
        return str(self._jsons)

    @with_lock
    def __getitem__(self, item):
        return self._jsons.get(item)

    @with_lock
    def __setitem__(self, key, value):
        self._jsons[key] = value

    @with_lock
    def get(self, key):
        return self._jsons.get(key)

    @with_lock
    def add(self, key, json):
        self._jsons[key].append(json)

    @with_lock
    def adds(self, key, jsons):
        self._jsons[key] += jsons

    @with_lock
    def update(self, jsons_dictionary):
        for key, json_list in jsons_dictionary.items():
            self.adds(key, json_list)

    @with_lock
    def to_dict(self):
        return self._jsons

    @with_lock
    def clear(self):
        self._jsons = dict.fromkeys(list(AQW_PACKETS.keys()), [])

    @with_lock
    def pop(self, key):
        return self._jsons.pop(key)

    @with_lock
    def pop_all(self):
        jsons = self._jsons
        self._jsons = dict.fromkeys(list(AQW_PACKETS.keys()), [])
        return jsons


class Interpreter(Processor):

    def __init__(self, character, sniffer):
        super().__init__(sniffer)
        self.character = character

    def parse_buffer_once(self):
        json = super().parse_buffer_once()
        return json['b']['o']

    def add_item(self, item_json):
        item_id = list(item_json.get('items').keys())[0]
        name = item_json.get('items').get(item_id).get('sName')
        iQty = item_json.get('items').get(item_id).get('iQty')
        self.character.add_item(item_id=item_id, name=name, iQty=iQty)
        iQtyNow = item_json.get('items').get(item_id).get('iQtyNow', None)
        if iQtyNow:
            self.character.set_inventory(item_id, iQtyNow)

    def add_drops(self, drop_json):
        item_id = list(drop_json.get('items').keys())[0]
        name = drop_json.get('items').get(item_id).get('sName')
        iQty = drop_json.get('items').get(item_id).get('iQty')
        self.character.add_drop(item_id=item_id, name=name, iQty=iQty)

    def add_kill(self, kill_json):
        kill_json.get('id')
        self.character.kill()

    def adjust_haste(self, stat_update_json):
        haste = stat_update_json.get('sta').get('$tha')
        if haste:
            self.character.haste = haste

    def parse_buffer(self, timeout=None):
        jsons = super().parse_buffer(timeout)
        for json in jsons:
            cmd = json.get('cmd')
            if cmd == AQW_PACKETS.get('addItems'):
                self.add_item(json)
            elif cmd == AQW_PACKETS.get('addDrop'):
                self.add_drops(json)
            elif cmd == AQW_PACKETS.get('stu'):
                self.adjust_haste(json)
