from handlers.ConfigHandler import *
import time


_config = get_config('classes.toml')
CLASS_ACRONYMS = Constant(_config.get('ACRONYMS'))
CLASS_ABILITIES = Constant(_config.get('ABILITIES'))
ALL_ABILITY_KEYS = ('1', '2', '3', '4', '5', '6')
SPECIAL_ABILITY_KEYS = ('2', '3', '4', '5')
POTION_KEY = '6'


def timeout_condition(t, start_time, timeout):
    if timeout:
        return t - start_time < timeout
    else:
        return True


def initialize(abilities):
    for ability in abilities.values():
        ability['_time'] = None


def get_ability(cd: float, name: str, mana: int, key: str):
    return {'cd': cd, 'name': name, 'key': key, 'mana': mana, '_time': None}


class CombatKit:

    @classmethod
    def load(cls, class_name, haste: float = 0):
        class_name = class_name.upper()
        class_name = CLASS_ACRONYMS.get(class_name, class_name)
        abilities = CLASS_ABILITIES.get(class_name)
        return cls(class_name=class_name, abilities=abilities, haste=haste)

    def __init__(self, *, class_name, abilities, haste=0.0):
        self._class = class_name
        self._abilities = abilities
        initialize(self._abilities)
        self._haste = min(haste, 0.5)
        self._mana = 100
        self._gcd = 1.5
        self._kills = {}
        self._combat_data = {'crit': 0, 'miss': 0, 'dodge': 0, 'enemy dodge': 0, 'total': 0, 'enemy total': 0}
        self._polling_delay = 0.01

    @property
    def abilities(self):
        return self._abilities

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
        self._haste = haste

    @property
    def cooldown_reduction(self):
        return 1 - self._haste

    @property
    def gcd(self):
        return self._gcd

    def get_kills(self, monster_gid):
        return self._kills.get(monster_gid)

    def add_combat_data(self, key, n=1):
        try:
            self._combat_data[key] += n
        except KeyError:
            raise ValueError("Use 'crit', 'miss', 'dodge', 'enemy dodge', 'total', or 'enemy total' as key.")

    def add_kills(self, monster_gid, n):
        self._kills.setdefault(monster_gid, 0)
        self._kills[monster_gid] += n

    def wait(self, keys=None, timeout=None):
        start_time = time.time()
        current_time = start_time
        while timeout_condition(current_time, start_time, timeout):
            for key in keys:
                time.sleep(self._polling_delay)
                ability = self._abilities.get(key)
                current_time = time.time()
                if current_time - ability.get('_time') > ability.get('cd') * self.cooldown_reduction:
                    ability['_time'] = None
                    return key
        return None

    def sleep_gcd(self):
        start_time = time.time()
        end_time = start_time
        while end_time - start_time < self._gcd * self.cooldown_reduction:
            time.sleep(self._polling_delay)
            end_time = time.time()

    def attack(self, key=None):
        ability = self._abilities.get(key)
        current_time = time.time()
        if ability is None  :
            raise ValueError('Invalid key.')
        elif ability.get('_time'):
            if current_time - ability.get('_time') > ability.get('cd') * self.cooldown_reduction:
                ability['_time'] = current_time
                self._mana = max(0, self._mana - ability.get('mana'))
        else:
            ability['_time'] = current_time
            self._mana = max(0, self._mana - ability.get('mana'))

