from network.processing import Processor
from game.character import Character
from game.aqw_backend import *
from threading import Lock
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

    @needs_character_initialized
    def add_item(self, item_json):
        item_id = list(item_json.get('items').keys())[0]
        name = item_json.get('items').get(item_id).get('sName')
        iQty = item_json.get('items').get(item_id).get('iQty')
        self.character.add_item(item_id=item_id, name=name, iQty=iQty)
        iQtyNow = item_json.get('items').get(item_id).get('iQtyNow', None)
        if iQtyNow:
            self.character.set_inventory(item_id, iQtyNow)

    @needs_character_initialized
    def add_drops(self, drop_json):
        item_id = list(drop_json.get('items').keys())[0]
        name = drop_json.get('items').get(item_id).get('sName')
        iQty = drop_json.get('items').get(item_id).get('iQty')
        self.character.add_drop(item_id=item_id, name=name, iQty=iQty)

    @needs_character_initialized
    def add_kill(self, kill_json):
        kill_json.get('id')
        self.character.kill()

    @needs_character_initialized
    def adjust_haste(self, stat_update_json):
        haste = stat_update_json.get('sta').get('$tha')
        if haste:
            self.character.haste = haste

    def initialize_character(self, json, parameters):
        cmd = json.get('cmd')
        match cmd:
            case 'stu':
                parameters['haste'] = json.get('sta').get('$tha')
                json = None
            case 'moveToArea':
                parameters['location'] = json.get('areaName')
                json = None
            case 'updateClass':
                parameters['class_name'] = json.get('sClassName')
                json = None
        if all(parameters.values()):
            self.character = Character(**parameters)
        return json

    @needs_character_initialized
    def interpret(self, json):
        cmd = json.get('cmd')
        match cmd:
            case 'addItems':
                self.add_item(json)
            case 'addDrop':
                self.add_drops(json)
            case 'stu':
                self.adjust_haste(json)

    def parse_buffer(self, timeout=None):
        parameters = {'class_name': None, 'haste': None, 'location': None}
        jsons = super().parse_buffer(timeout)
        for json in jsons:
            if not self.character:
                json = self.initialize_character(json, parameters)
                if json:
                    jsons.append(json)
            else:
                self.interpret(json)

