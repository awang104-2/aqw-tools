from threads.custom_threading import *
from handlers.DictHandler import *
import toml
import os


class Quest:

    _config_path = os.path.join(os.path.dirname(__file__), 'config', 'quests.toml')
    _quest_config = toml.load(_config_path)

    def __init__(self, name, requirements, cap):
        self.name = name.upper()
        self.requirements = deepcopy(requirements)
        self.cap = deepcopy(cap)
        self.progress = dict.fromkeys(self.requirements, 0)
        self.num_completed = 0

    @classmethod
    def load(cls, name):
        quest_details = Quest._quest_config.get(name)
        name = name.upper()
        requirements = quest_details.get('REQUIREMENTS')
        cap = quest_details.get('CAP')
        return cls(name=name, requirements=requirements, cap=cap)

    def get_item_ids(self):
        return list(self.requirements.keys())

    def is_required_item(self, item_id):
        return item_id in self.get_item_ids()

    def add(self, item_id, number):
        self.progress[item_id] += number

    def print(self):
        print(f'{self.name}')
        for item_id, num in self.progress.items():
            print(f'{item_id}: {num}')

    def check_quest(self):
        quests_satisfied = 0
        for item_id, condition in self.requirements.items():
            condition_satisfied = int(self.progress.get(item_id) / condition)
            if condition_satisfied < quests_satisfied:
                quests_satisfied = condition_satisfied
        return quests_satisfied

    def complete(self, n):
        for item_id in self.progress.keys():
            self.progress[item_id] -= n * self.requirements.get(item_id)
            if self.progress.get(item_id) < 0:
                raise ValueError('Argument \'n\' is too large, not enough quests completed.')
        self.num_completed += n

    def copy(self):
        return Quest(name=self.name, requirements=self.requirements, cap=self.cap)


class Quests:

    @classmethod
    def from_names(cls, names):
        if not all(isinstance(name, str) for name in names):
            raise TypeError('Arguments must be strings.')
        quests = [Quest.load(name) for name in names]
        return cls(quests)

    def __init__(self, quests):
        if not all(isinstance(quest, Quest) for quest in quests):
            raise TypeError('Arguments must be strings.')
        self.quests = quests

    def get_quest(self, name: str):
        for quest in self.quests:
            if name == quest.name:
                return quest

    def get_quests(self, names: list | tuple):
        quests = []
        for quest in self.quests:
            if quest.name in names:
                quests.append(quest)
        return quests

    def get_quest_names(self):
        return [quest.name for quest in self.quests]

    def check_quests(self):
        quests_satisfied = {}
        for quest in self.quests:
            quests_satisfied[quest.name] = quest.check_quest()
        return quests_satisfied

    def complete(self, names: str | list | tuple, n: int):
        if isinstance(names, str):
            names = [names]
        for quest in self.get_quests(names):
            quest.complete(n)


class Combat:

    _config_path = os.path.join(os.path.dirname(__file__), 'config', 'classes.toml')
    _combat_config = toml.load(_config_path)
    _class_info = _combat_config.get('CLASS INFO')
    _class_acronyms = _combat_config.get('ACRONYMS')

    @staticmethod
    def _get_ability_info(cd: float, name: str, mana: int, key: str, speed: float):
        timer = AdjustableTimer(interval=cd, name=f'ability-{key} cd', daemon=True, speed=speed)
        return {'cd': cd, 'timer': timer, 'name': name, 'key': key, 'mana': mana}

    @staticmethod
    def _abilities_to_dict(abilities, speed=1):
        dictionary = {}
        for key, info in abilities.items():
            dictionary[key] = Combat._get_ability_info(**info, speed=speed)
        return dictionary

    @classmethod
    def load(cls, class_name, haste: float = 0):
        class_name = class_name.upper()
        class_name = Combat._class_acronyms.get(class_name, class_name)
        class_info = {'class_name': class_name}
        class_info.update(Combat._class_info.get(class_name))
        return cls(**class_info, haste=haste)

    def __init__(self, *, class_name, haste, rotation, rotation_type, abilities, gcd):
        self._class = class_name
        self._haste = min(haste, 0.5)
        self._rotation = rotation
        self._rotation_type = rotation_type
        self._abilities = Combat._abilities_to_dict(abilities, self.cooldown_speed)
        self._gcd = gcd
        self._kills = 0
        self._combat_data = {'crit': 0, 'miss': 0, 'dodge': 0, 'enemy dodge': 0, 'total': 0, 'enemy total': 0}

    @property
    def total(self):
        return self._combat_data.get('hit')

    @property
    def enemy_total(self):
        return self._combat_data.get('enemy hit')

    @property
    def crit_chance(self):
        total = self.total
        if total > 0:
            return self._combat_data.get('crit') / total
        else:
            return None

    @property
    def dodge_chance(self):
        enemy_total = self.total
        if enemy_total > 0:
            return self._combat_data.get('dodge') / enemy_total
        else:
            return None

    @property
    def haste(self):
        return self._haste

    @haste.setter
    def haste(self, haste):
        haste = min(haste, 0.5)
        if self._haste != haste:
            self._haste = haste
            for ability in self._abilities.values():
                ability.get('timer').adjust(self.cooldown_speed)

    @property
    def cooldown_reduction(self):
        return 1 - self._haste

    @property
    def cooldown_speed(self):
        return 1 / self.cooldown_reduction

    @property
    def original_gcd(self):
        return self._gcd

    @property
    def reduced_gcd(self):
        return self._gcd * self.cooldown_reduction

    def add_combat_data(self, key, n):
        self._combat_data[key] += n

    def add_kills(self, n):
        self._kills += n

    def get_kills(self):
        return self._kills

    def get_move(self, key):
        return deepcopy(self._get_move(key))

    def _get_move(self, key):
        key = str(key)
        return self._abilities.get(key)

    def _rotate(self):
        last_key = self._rotation.pop(0)
        self._rotation = self._rotation + [last_key]

    def _find_first_ready(self):
        for key in self._rotation:
            if self._abilities.get(key).get('timer').ready:
                return key
        return None

    def sleep_gcd(self):
        t, t0 = 0, time()
        while t < self.reduced_gcd:
            sleep(0.05)
            t = time() - t0

    def _use_ability_rotation(self, key):
        ability = self._abilities.get(key)
        if not ability.get('timer').ready:
            self.sleep_gcd()
            ability.get('timer').wait_until_ready()
        ability.get('timer').start()
        return ability.get('key')

    def _use_ability_priority(self, key):
        ability = self._abilities.get(key)
        if not ability:
            return ability
        ability.get('timer').start()
        return ability.get('key')

    def _attack_rotation(self):
        key = self._use_ability_rotation(self._rotation[0])
        self._rotate()
        return key

    def _attack_priority(self):
        key = self._find_first_ready()
        self._use_ability_priority(key)
        return key

    def attack(self, func=None):
        if self._rotation_type == 'rotation':
            key = self._attack_rotation()
        elif self._rotation_type == 'priority':
            key = self._attack_priority()
        else:
            raise ValueError('Rotation type must be \'priority\' or \'rotation\'.')
        if func:
            func(key)
        self.sleep_gcd()


class Item:

    _config_path = os.path.join(os.path.dirname(__file__), 'config', 'drops.toml')


class Inventory:

    _config_path = os.path.join(os.path.dirname(__file__), 'config', 'drops.toml')
    _sampling_path = os.path.join(os.path.dirname(__file__), 'config', 'sampling.toml')

    @staticmethod
    def get_db():
        with open(Inventory._config_path, 'r') as file:
            drop_config = toml.load(file)
        return drop_config

    @staticmethod
    def write_db(db):
        with open(Inventory._config_path, 'w') as file:
            toml.dump(db, file)

    def __init__(self):
        self.inventory = {}
        self.drops = {}

    def __str__(self):
        return f'Drops: {self.drops}\nInventory: {self.inventory}'

    def set_inventory(self, item_id, iQtyNow):
        self.inventory[item_id]['count'] = iQtyNow

    def add(self, item_id, name, iQty):
        if self.drops.get(item_id, False):
            self.drops[item_id]['count'] += iQty
            self.inventory[item_id]['count'] += iQty
        else:
            self.drops[item_id] = {'name': name, 'count': iQty}
            self.inventory[item_id] = {'name': name, 'count': iQty}
        if not self.drops.get(item_id).get('name'):
            self.drops[item_id]['name'] = name
            self.inventory[item_id]['name'] = name

    def subtract(self, item_id, iQty):
        self.drops[item_id] -= iQty

    def get_drops(self):
        return self.drops.copy()

    def get_drop(self, item_id):
        return self.drops.get(item_id, None)

    def get_inventory(self):
        return self.inventory.copy()

    def reset(self):
        for key in self.inventory.keys():
            self.inventory[key]['count'] = 0
        for key in self.drops.keys():
            self.drops[key]['count'] = 0

    def save(self, filepath=None):
        if not filepath:
            filepath = Inventory._sampling_path
        drops = self.get_drops()
        for item_id in drops.keys():
            if not drops.get(item_id).get('name'):
                drops[item_id]['name'] = 'None'
        with open(filepath, 'w') as file:
            toml.dump(drops, file)

    def merge_db(self, filepath=None):
        db = self.get_db()
        if not filepath:
            filepath = Inventory._sampling_path
        with open(filepath, 'r') as file:
            data = toml.load(file)
        for key, value in data.items():
            if value.get('name') != 'None' and db.get(key) and db.get(key).get('name') == 'None':
                db[key]['name'] = value.get('name')
            elif not db.get(key):
                db[key] = {'name': value.get('name')}
        self.write_db(db)


class Location:

    @staticmethod
    def parse_location(location):
        map_name, lobby_num = location.split('-')
        return map_name, lobby_num

    @classmethod
    def load(cls, location):
        map_name, lobby_num = Location.parse_location(location)
        return cls(map_name=map_name, lobby_num=lobby_num)

    def __init__(self, map_name='battleon', lobby_num='1'):
        self._map = map_name.lower()
        self._lobby = lobby_num

    def __str__(self):
        return f'{self._map}-{self._lobby}'

    @property
    def lobby(self):
        return self._lobby

    @property
    def map(self):
        return self._map

    def __self__(self, location):
        self._map, self.lobby_num = Location.parse_location(location)
        return self._map

