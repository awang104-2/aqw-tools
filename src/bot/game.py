from time import sleep
from threads.custom_threads import *
import toml
import os


config_path = os.path.join(os.path.dirname(__file__), 'config')


class Quest:

    def __configure(self, names):
        quests_config_path = os.path.join(config_path, 'quests.toml')
        with open(quests_config_path, 'r') as file:
            quest_config = toml.load(file)
        for name in names:
            name = name.upper()
            self.requirements[name] = quest_config[name]
            self.completed[name] = 0

    def __init__(self, names=None, quest_ids=None):
        self.requirements = {}
        self.completed = {}
        self.quest_ids = quest_ids
        self.__configure(names)

    def get_quest_names(self):
        return list(self.requirements.keys())

    def check_quest(self, drops):
        total_turn_ins = {}
        for name in self.requirements.keys():
            turn_ins = 0
            item_reqs = self.requirements.get(name)
            item_ids = item_reqs.keys()
            for i, item_id in enumerate(list(item_ids)):
                drop, req, cap = drops.get_drop(item_id), item_reqs.get(item_id)[0], item_reqs.get(item_id)[1]
                if not drop or drop.get('count') - req * self.completed.get(name) < cap:
                    turn_ins = 0
                    break
                else:
                    req_done = int(drop.get('count') / req) - self.completed.get(name)
                    if i == 0:
                        turn_ins = int(drop.get('count') / req) - self.completed.get(name)
                    elif turn_ins > req_done:
                        turn_ins = req_done
            total_turn_ins[name] = turn_ins
            self.turn_in(name, turn_ins)
        return total_turn_ins

    def turn_in(self, name, num):
        self.completed[name] += num

    def get_req_ids(self):
        item_ids = []
        for name in self.get_quest_names():
            item_ids += list(self.requirements.get(name).keys())
        return item_ids

class Combat:

    classes = {'AM': 'ARCHMAGE', 'AI': 'ARCANA INVOKER', 'LR': 'LEGION REVENANT', 'AF': 'ARCHFIEND'}

    def __configure(self):
        classes_config_path = os.path.join(config_path, 'classes.toml')
        with open(classes_config_path, 'r') as file:
            class_config = toml.load(file).get(self.cls)
        self.rotation = class_config.get('rotation')
        self.rotation_type = class_config.get('rotation_type')
        self.gcd = class_config.get('gcd')
        self.info = {
            '1': {'cd': class_config['1']['cd'] * self.cd_reduction, 'status': CustomEvent(True),
                  'timer': CustomTimer(name='ability-1 cd')},
            '2': {'cd': class_config['2']['cd'] * self.cd_reduction, 'status': CustomEvent(True),
                  'timer': CustomTimer(name='ability-2 cd')},
            '3': {'cd': class_config['3']['cd'] * self.cd_reduction, 'status': CustomEvent(True),
                  'timer': CustomTimer(name='ability-3 cd')},
            '4': {'cd': class_config['4']['cd'] * self.cd_reduction, 'status': CustomEvent(True),
                  'timer': CustomTimer(name='ability-4 cd')},
            '5': {'cd': class_config['5']['cd'] * self.cd_reduction, 'status': CustomEvent(True),
                  'timer': CustomTimer(name='ability-5 cd')}
        }

    def __init__(self, cls, haste=0.5):
        self.cd_reduction = 1 - haste
        self.kills = 0
        self.cls = cls.upper()
        if self.cls in list(Combat.classes.keys()):
            self.cls = Combat.classes.get(self.cls)
        elif self.cls in list(Combat.classes.values()):
            pass
        else:
            raise ValueError('Class not found.')
        self.__configure()
        self.__set_timers()

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

    def __set_timers(self):
        for key in self.rotation:
            move = self.get_move(key)
            status = move.get('status')
            cooldown = move.get('cd')
            timer = move.get('timer')
            timer.set_parameters(cooldown, status.set, True, key)

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


class Inventory:

    __drops_config_path = os.path.join(config_path, 'drops.toml')

    @staticmethod
    def get_db():
        with open(Inventory.__drops_config_path, 'r') as file:
            drop_config = toml.load(file)
        return drop_config

    @staticmethod
    def write_db(db):
        with open(Inventory.__drops_config_path, 'w') as file:
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

    def save(self, path=None):
        if not path:
            path = os.path.join(config_path, 'drops_samples.toml')
        drops = self.get_drops()
        for item_id in drops.keys():
            if not drops.get(item_id).get('name'):
                drops[item_id]['name'] = 'None'
        with open(path, 'w') as file:
            toml.dump(drops, file)

    def merge_db(self, filepath=None):
        db = self.get_db()
        if not filepath:
            filepath = os.path.join(config_path, 'drops_samples.toml')
        with open(filepath, 'r') as file:
            data = toml.load(file)
        for key, value in data.items():
            if not db.get(key):
                db[key] = value
        self.write_db(db)


