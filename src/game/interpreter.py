from network.processing import Processor
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

    @needs_character_initialized
    def add_item(self, item_json):
        item_id = list(item_json.get('items').keys())[0]
        name = item_json.get('items').get(item_id).get('sName')
        quantity = item_json.get('items').get(item_id).get('iQty')
        self.character.add(item_id=item_id, name=name, quantity=quantity)
        inventory_quantity = item_json.get('items').get(item_id).get('iQtyNow')
        if inventory_quantity:
            self.character.set_inventory(item_id, inventory_quantity)

    def add_drops(self, drop_json):
        item_id = list(drop_json.get('items').keys())[0]
        name = drop_json.get('items').get(item_id).get('sName')
        quantity = drop_json.get('items').get(item_id).get('iQty')
        self.character.add(item_id=item_id, name=name, quantity=quantity)

    def add_kill(self, kill_json):
        local_id = kill_json.get('id')
        if local_id:
            self.character.kill(local_id)

    def adjust_haste(self, stat_update_json):
        haste = stat_update_json.get('sta').get('$tha')
        if haste:
            self.character.haste = haste

    def update_location(self, loc_json):
        location = loc_json.get('areaName')
        self.character.reinitialize(location=location)

    def update_class(self, class_json):
        class_name = class_json['sClassName']
        if class_json.get('sDesc'):
            self.character.reinitialize(class_name=class_name)

    def add_rewards(self, reward_json):
        self.add_kill(reward_json)

    def update_combat_data(self, combat_json):
        try:
            hit_type = combat_json['sarsa'][0]['a'][0]['type']
            self.character.add_combat_data(hit_type)
        except KeyError:
            pass

    def update_class_skills(self, skill_data_json, force=False):
        if not force and self.character.is_class_defined():
            return
        skills = skill_data_json['actions']['active'][:5]
        abilities = {}
        for i, skill in enumerate(skills):
            key, cd, name, mana = str(i + 1), skill.get('cd') / 1000, skill.get('nam'), skill.get('mp')
            abilities[key] = self.character.create_ability(cd, name, mana, key)
        self.character.reinitialize(abilities=abilities)
        self.character.store()

    def interpret_from_json(self, json):
        cmd = json.get('cmd')
        match cmd:
            case 'moveToArea':
                self.update_location(json)
            case 'updateClass':
                self.update_class(json)
            case 'addItems':
                self.add_item(json)
            case 'addDrop':
                self.add_drops(json)
            case 'stu':
                self.adjust_haste(json)
            case 'addGoldExp':
                self.add_rewards(json)
            case 'ct':
                self.update_combat_data(json)
            case 'sAct':
                self.update_class_skills(json)

    def interpret(self):
        try:
            extended_json = self.jsons.get(timeout=self.timeout)
            json = extended_json['b']['o']
            self.interpret_from_json(json)
        except Processor.EmptyError:
            pass
        except KeyError:
            self.missed_packets += 1

