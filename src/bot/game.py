from threading import Event, Timer


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

    def __init__(self, cls):
        if cls.lower() not in Combat.classes:
            raise ValueError('Find')
        self.cls = cls.lower()
        self.info = {'1': {'cd': 1, 'status': Event()}, '2': {'cd': 1, 'status': Event()}, '3': {'cd': 1, 'status': Event()}, '4': {'cd': 1, 'status': Event()}, '5': {'cd': 1, 'status': Event()}}
        self.combo = ['1', '2', '3', '4', '5']
        self.rotation_type = 'rotation'
        self.kills = 0

    def add_kills(self, data):
        if data.get('cmd') != 'addGoldExp':
            raise ValueError(f'Wrong JSON type: {data.get('cmd')}')
        self.kills += 1

    def get_kills(self):
        return self.kills

    def get_move(self, move):
        move = str(move)
        return self.info.get(move, None)

    def fight(self):
        move = self.combo[0]
        status = self.info.get(move).get('status')
        cooldown = self.info.get(move).get('cd')
        status.wait()
        self.combo = self.combo[1:] + [move]
        Timer(cooldown, status.set).start()
        status.clear()
        return move


class Drops:

    def __init__(self):
        self.drops = {}

    def add(self, item_id, name, iQty):
        if self.drops.get(item_id, None):
            self.drops[item_id]['count'] += iQty
        else:
            self.drops[item_id] = {'name': name, 'count': num}

    def get_drops(self):
        return self.drops.copy()

    def get_drop(self, item_id):
        return self.drops.get(item_id, None)

    def reset(self):
        self.drops = {}



