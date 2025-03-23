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
    _class_config = toml.load(_config_path)

    @staticmethod
    def _get_ability_info(cd: float, name: str, mana: int, key: str):
        status = CustomEvent(True)
        timer = CustomTimer(interval=cd, function=status.set, name=f'ability-{key} cd', daemon=True)
        return {'cd': cd, 'status': status, 'timer': timer, 'name': name, 'key': key, 'mana': mana}

    def __init__(self, cls: str, haste: int, rotation: tuple | list, rotation_type: str, cd1: int, cd2: int, cd3: int, cd4: int, cd5: int, gcd: int):
        self.cls = cls
        self.cd_reduction = 1 - haste
        self.kills = 0
        self.rotation = deepcopy(rotation)
        self.rotation_type = rotation_type
        self.gcd = gcd
        self.info = {
            '1': {'cd': cd1 * self.cd_reduction, 'status': CustomEvent(True), 'timer': None},
            '2': {'cd': cd2 * self.cd_reduction, 'status': CustomEvent(True), 'timer': None},
            '3': {'cd': cd3 * self.cd_reduction, 'status': CustomEvent(True), 'timer': None},
            '4': {'cd': cd4 * self.cd_reduction, 'status': CustomEvent(True), 'timer': None},
            '5': {'cd': cd5 * self.cd_reduction, 'status': CustomEvent(True), 'timer': None}
        }
        self._set_timers()

    def load(self, cls, haste):
        class_name = Combat._class_config.get('ACRONYMS').get(cls, cls)
        class_details = Combat._class_config.get(cls)

    def _set_timers(self):
        for ability, ability_info in self.info.items():
            interval = ability_info.get('cd')
            function = ability_info.get('status').set
            name = f'ability-{ability} cd'
            daemon = True
            ability_info['timer'] = CustomTimer(interval=interval, function=function, name=name, daemon=daemon)

    def add_kills(self, n):
        self.kills += n

    def get_kills(self):
        return self.kills

    def get_move(self, key):
        key = str(key)
        return self.info.get(key)

    def increment_move(self):
        key = self.rotation[0]
        if self.rotation_type == 'rotation':
            self.rotation = self.rotation[1:] + [key]
        return key

    def check_moves(self):
        for move in self.rotation:
            status = self.get_move(move).get('status')
            if status.is_set():
                return move
        return None

    def sleep_gcd(self):
        sleep(self.gcd * self.cd_reduction)


    def fight(self):
        if self.rotation_type == 'rotation':
            key = self.increment_move()
            move = self.get_move(key)
            status = move.get('status')
            timer = move.get('timer')
            timer.start()
            status.wait()
            status.clear()
            return key
        elif self.rotation_type == 'priority':
            key = self.check_moves()
            if key:
                move = self.get_move(key)
                status = move.get('status')
                timer = move.get('timer')
                timer.start()
                status.clear()
                return key
            else:
                return None
        else:
            raise ValueError('Rotation type must be \'priority\' or \'rotation\'.')


class Item:

    __config_path = os.path.join(os.path.dirname(__file__), 'config', 'drops.toml')




class Inventory:

    __config_path = os.path.join(os.path.dirname(__file__), 'config', 'drops.toml')
    __sampling_path = os.path.join(os.path.dirname(__file__), 'config', 'sampling.toml')

    @staticmethod
    def get_db():
        with open(Inventory.__config_path, 'r') as file:
            drop_config = toml.load(file)
        return drop_config

    @staticmethod
    def write_db(db):
        with open(Inventory.__config_path, 'w') as file:
            toml.dump(db, file)

    def __init__(self):
        self.inventory = {}
        self.drops = {}

    def __str__(self):
        return f'Drops: {self.drops}\nInventory: {self.inventory}'

    def set_inventory(self, item_id, iQtyNow):
        self.inventory[item_id]['count'] = iQtyNow

    def add(self, item_id, name, iQty, quest_reqs):
        if self.drops.get(item_id, False):
            self.drops[item_id]['count'] += iQty
            self.inventory[item_id]['count'] += iQty
        else:
            self.drops[item_id] = {'name': name, 'count': iQty}
            self.inventory[item_id] = {'name': name, 'count': iQty}
        if not self.drops.get(item_id).get('name'):
            self.drops[item_id]['name'] = name
            self.inventory[item_id]['name'] = name
        return item_id in quest_reqs

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
            filepath = Inventory.__sampling_path
        drops = self.get_drops()
        for item_id in drops.keys():
            if not drops.get(item_id).get('name'):
                drops[item_id]['name'] = 'None'
        with open(filepath, 'w') as file:
            toml.dump(drops, file)

    def merge_db(self, filepath=None):
        db = self.get_db()
        if not filepath:
            filepath = Inventory.__sampling_path
        with open(filepath, 'r') as file:
            data = toml.load(file)
        for key, value in data.items():
            if value.get('name') != 'None' and db.get(key) and db.get(key).get('name') == 'None':
                db[key]['name'] = value.get('name')
            elif not db.get(key):
                db[key] = {'name': value.get('name')}
        self.write_db(db)


