from network.processing import Processor
from game.game_sniffer import GameSniffer
from threading import Thread, Event


SENTINEL = 'STOP COMMAND INTERPRETER'


class Interpreter:

    def __init__(self, character, server, daemon=False):
        self.character = character
        self.sniffer = GameSniffer(server=server, daemon=True)
        self.processor = Processor(self.sniffer, daemon=True)
        self._interpreter = Thread(target=self.interpret, name='Interpreting Thread', daemon=daemon)
        self._flag = Event()

    @property
    def daemon(self):
        return self._interpreter.daemon

    @daemon.setter
    def daemon(self, daemon):
        self._interpreter.daemon = daemon

    @property
    def running(self):
        return self._interpreter.is_alive()

    def connect(self):
        self.sniffer.start()
        self.processor.start()

    def disconnect(self):
        self.sniffer.stop()
        self.processor.stop()

    def start(self):
        self._flag.set()
        self._interpreter.start()

    def stop(self, timeout=None):
        self._flag.clear()
        self.processor.jsons.put(SENTINEL)
        self._interpreter.join(timeout)

    def connected(self, process: str):
        match process:
            case 'sniffer':
                return self.sniffer.running
            case 'processor':
                return self.processor.running
            case 'both':
                return self.sniffer.running and self.processor.running
        raise ValueError('Argument must be \'sniffer\', \'processor\', or \'both\'.')

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

    def update_location(self, location_json):
        location = location_json.get('areaName')
        monsters = {}
        monster_info = location_json.get('mondef')
        if monster_info:
            map_ids = location_json['monmap']
            for i, monster in enumerate(monster_info):
                monster_id = monster['MonID']
                name = monster['strMonName']
                map_id = map_ids[i]['MonMapID']
                if monster_id == map_ids[i]['MonID']:
                    monsters[map_id] = name
            print(monsters)
        self.character.reinitialize(location=location, monsters=monsters)
        self.character.store('location')

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
        self.character.store('combat kit')

    def reset(self, server):
        if server:
            self.sniffer = GameSniffer(server=server)
            self.processor = Processor(self.sniffer)
        daemon = self._interpreter.daemon
        self._interpreter = Thread(target=self.interpret, name='Interpreting Thread', daemon=daemon)
        self._flag.clear()

    def interpret(self):
        while self._flag.is_set():
            json = self.processor.get()
            if json == SENTINEL:
                continue
            json = json['b']['o']
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

    def join(self, timeout=None):
        self.sniffer.join(timeout)
        self.processor.join(timeout)
        self._interpreter.join(timeout)
