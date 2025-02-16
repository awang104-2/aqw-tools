from time import sleep
from threads.custom_threads import *


class Quest:

    def __init__(self, name=None, quest_id=None):
        if not (quest_id or name):
            raise ValueError('Must specify the quest ID or the name of the quest.')
        self.requirements = {'6135': 1, '15385': 5}
        self.quest_id = {'QuestID': 2566, 'sName': 'Nulgath\'s Roulette of Misfortune'}

    def check_quest(self, drops):
        for i, item_id in enumerate(list(self.requirements.keys())):
            drop, requirement = drops.get_drop(item_id), self.requirements.get(item_id)
            if drop and drop.get('count') >= requirement:
                req_completed = int(drop.get('count') / requirement)
                if i == 0:
                    num_completed = req_completed
                elif num_completed > req_completed:
                    num_completed = req_completed
                continue
            else:
                return False, 0
        return True, num_completed

    def turn_in(self, drops, num):
        for i, item_id in enumerate(list(self.requirements.keys())):
            requirement = drops.get_drop(item_id)
            completed = requirement * num
            drops[item_id] -= completed
            

class Combat:

    classes = ['archmage', 'am', 'arcana invoker', 'ai']

    def __init__(self, cls, haste=0.5):
        if cls.lower() not in Combat.classes:
            raise ValueError('Find')
        self.cls = cls.lower()
        self.cd_reduction = 1 - haste
        self.combo = ['4', '5', '2', '3', '1']
        self.rotation_type = 'priority'
        self.kills = 0
        self.gcd = 1.5
        self.info = {
            '1': {'cd': 1.5 * self.cd_reduction, 'status': CustomEvent(True), 'timer': CustomTimer()},
            '2': {'cd': 6 * self.cd_reduction, 'status': CustomEvent(True), 'timer': CustomTimer()},
            '3': {'cd': 6 * self.cd_reduction, 'status': CustomEvent(True), 'timer': CustomTimer()},
            '4': {'cd': 6 * self.cd_reduction, 'status': CustomEvent(True), 'timer': CustomTimer()},
            '5': {'cd': 12 * self.cd_reduction, 'status': CustomEvent(True), 'timer': CustomTimer()}
        }
        self.__set_timers()

    def add_kills(self, data):
        if data.get('cmd') != 'addGoldExp':
            raise ValueError(f'Wrong JSON type: {data.get('cmd')}')
        self.kills += 1

    def get_kills(self):
        return self.kills

    def get_move(self, key):
        key = str(key)
        return self.info.get(key)

    def increment_move(self):
        key = self.combo[0]
        if self.rotation_type == 'rotation':
            self.combo = self.combo[1:] + [key]
        return key

    def check_moves(self):
        for move in self.combo:
            status = self.get_move(move).get('status')
            if status.is_set():
                return move
        return None

    def sleep_gcd(self):
        sleep(self.gcd * self.cd_reduction)

    def __set_timers(self):
        for key in self.combo:
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
            sleep(0.1)
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


class Drops:

    def __init__(self):
        self.drops = {}

    def add(self, item_id, name, iQty):
        if self.drops.get(item_id, None):
            self.drops[item_id]['count'] += iQty
        else:
            self.drops[item_id] = {'name': name, 'count': iQty}

    def get_drops(self):
        return self.drops.copy()

    def get_drop(self, item_id):
        return self.drops.get(item_id, None)

    def reset(self):
        self.drops = {}





