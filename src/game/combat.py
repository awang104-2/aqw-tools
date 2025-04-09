from handlers.ConfigHandler import *
import math
import time


_config = get_config('classes.toml')
CLASS_ACRONYMS = SafeDict(_config.get('ACRONYMS'))
CLASS_ABILITIES = SafeDict(_config.get('ABILITIES'))
ALL_ABILITY_KEYS = ('1', '2', '3', '4', '5', '6')
SPECIAL_ABILITY_KEYS = ('2', '3', '4', '5')
POTION_KEY = '6'


def from_acronym(class_acronym):
    class_acronym = class_acronym.upper()
    class_name = CLASS_ACRONYMS.get(class_acronym, class_acronym)
    return class_name


def loads(class_name=None):
    class_name = from_acronym(class_name)
    abilities = CLASS_ABILITIES.get(class_name)
    return class_name, abilities


def timeout_condition(t, start_time, timeout):
    if timeout:
        return t - start_time < timeout
    else:
        return True


def get_ability(cd: float, name: str, mana: int, key: str):
    return {'cd': cd, 'name': name, 'key': key, 'mana': mana, '_time': None}


class InvalidClassError(TypeError):

    def __init__(self, class_name):
        valid_classes = CLASS_ACRONYMS.values()
        string = f'\'{class_name}\' is not a valid class name. Use one from {valid_classes}.'
        super().__init__(string)


class CombatKit:

    @classmethod
    def load(cls, class_name=None, haste=0):
        abilities = None
        if class_name:
            class_name, abilities = loads(class_name)
        return CombatKit(class_name, abilities=abilities, haste=haste)

    def __init__(self, class_name: str = None, *, abilities: dict = None, haste: float = 0):
        self._class = class_name
        self._abilities = abilities
        self.initialize_abilities()
        self._haste = min(haste, 0.5)
        self._mana = 100
        self._gcd = 1.5
        self._kills = {}
        self._combat_data = {'crit': 0, 'miss': 0, 'dodge': 0, 'enemy dodge': 0, 'total': 0, 'enemy total': 0}
        self._polling_delay = 0.01

    def reinitialize(self, class_name, haste=None, deep=False):
        self._class, self._abilities = loads(class_name)
        self.initialize_abilities()
        if haste:
            self._haste = min(haste, 0.5)
        if deep:
            self._mana = 100
            self._gcd = 1.5
            self._kills = {}
            self._combat_data = {'crit': 0, 'miss': 0, 'dodge': 0, 'enemy dodge': 0, 'total': 0, 'enemy total': 0}
            self._polling_delay = 0.01

    def initialize_abilities(self):
        if not self._abilities:
            self.reinitialize('TEST CLASS')
        for ability in self._abilities.values():
            ability.update({'_time': None})

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
        self._haste = min(haste, 0.5)

    @property
    def cooldown_reduction(self):
        return 1 - self._haste

    @property
    def gcd(self):
        return self._gcd

    def get_kills(self, monster_id):
        return self._kills.get(monster_id)

    def add_combat_data(self, key, n=1):
        try:
            self._combat_data[key] += n
        except KeyError:
            raise ValueError("Use 'crit', 'miss', 'dodge', 'enemy dodge', 'total', or 'enemy total' as key.")

    def add_kills(self, monster_id, n):
        self._kills.setdefault(monster_id, 0)
        self._kills[monster_id] += n

    def wait(self, keys=None, timeout=None):
        start_time = time.time()
        current_time = start_time
        while timeout_condition(current_time, start_time, timeout):
            for key in keys:
                ability = self._abilities.get(key)
                if ability.get('_time'):
                    time.sleep(self._polling_delay)
                    current_time = time.time()
                    if current_time - ability.get('_time') > self.adjust_for_haste(ability.get('cd')):
                        ability['_time'] = None
                        return key
                else:
                    return key
        return None

    def adjust_for_haste(self, value):
        return math.ceil(value * self.cooldown_reduction * 100) / 100

    def sleep_gcd(self):
        start_time = time.time()
        current_time = start_time
        while current_time - start_time < self.adjust_for_haste(self._gcd):
            time.sleep(self._polling_delay)
            current_time = time.time()

    def attack(self, key=None):
        ability = self._abilities.get(key)
        current_time = time.time()
        if ability is None  :
            raise ValueError('Invalid key.')
        elif ability.get('_time'):
            if current_time - ability.get('_time') > self.adjust_for_haste(ability.get('cd')):
                ability['_time'] = current_time
                self._mana = max(0, self._mana - ability.get('mana'))
            else:
                raise RuntimeError(f'Ability-{key}: \'{ability.get('name')}\' is not ready.')
        else:
            ability['_time'] = current_time
            self._mana = max(0, self._mana - ability.get('mana'))

    def __str__(self):
        string = f'Class Name: {self._class}'
        for key, ability in self._abilities.items():
            string += f'\nAbility-{key}: {ability}'
        string += f'\nHaste: {self._haste}\nKills: {self._kills}\nCombat Data: {self._combat_data}'
        return string

