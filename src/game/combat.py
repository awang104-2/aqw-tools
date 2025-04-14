from handlers.ConfigHandler import *
from typing import Self
import math
import time


_config = get_config('classes.toml')
CLASS_ACRONYMS = SafeDict(_config.get('ACRONYMS'))
CLASS_NAMES = tuple(CLASS_ACRONYMS.values())
CLASS_ABILITIES = SafeDict(_config.get('ABILITIES'))
ALL_ABILITY_KEYS = ('1', '2', '3', '4', '5', '6')
SPECIAL_ABILITY_KEYS = ('2', '3', '4', '5')
MAIN_ABILITY_KEYS = ('1', '2', '3', '4', '5')
POTION_KEY = '6'


def from_acronym(class_acronym, upper=True):
    if upper:
        uppercased = class_acronym.upper()
        default = class_acronym.upper()
    else:
        uppercased = class_acronym.upper()
        default = class_acronym
    class_name = CLASS_ACRONYMS.get(uppercased, default)
    return class_name


def loads(class_name=None):
    class_name = from_acronym(class_name)
    abilities = CLASS_ABILITIES.get(class_name, {})
    return class_name, abilities


def timeout_condition(t, start_time, timeout):
    if timeout:
        return t - start_time < timeout
    else:
        return True


def _del_time(abilities):
    abilities_copy = copy.deepcopy(abilities)
    for ability in abilities_copy.values():
        del ability['_time']
    return abilities_copy


def get_ability(cd: float, name: str, mana: int, key: str):
    return {'cd': cd, 'name': name, 'mana': mana, 'key': key}


def _get_ability(cd: float, name: str, mana: int, key: str):
    return {'cd': cd, 'name': name, 'mana': mana, 'key': key, '_time': None}


def is_valid_ability(ability):
    return ability == get_ability(**ability)


def are_valid_abilities(abilities):
    if tuple(abilities.keys()) != MAIN_ABILITY_KEYS:
        return False
    for ability in abilities.values():
        if ability == get_ability(**ability):
            continue
        return False
    return True


def save_new_classes(abilities):
    write_to_config(abilities, 'new_classes.toml')


class InvalidClassError(TypeError):

    def __init__(self, class_name):
        valid_classes = CLASS_NAMES
        string = f'\'{class_name}\' is not a valid class name. Use one from {valid_classes}.'
        super().__init__(string)


class CombatKit:

    _new_classes = get_config('new_classes.toml')

    @staticmethod
    def save():
        write_to_config(CombatKit._new_classes, 'new_classes.toml')

    @classmethod
    def load(cls, class_name=None, haste=0) -> Self:
        abilities = None
        if class_name:
            class_name, abilities = loads(class_name)
        return CombatKit(class_name, abilities=abilities, haste=haste)

    def __init__(self, class_name: str | None = None, *, abilities: dict | None = None, haste: float = 0):
        self._class = class_name
        if abilities:
            self._abilities = abilities
        else:
            self._abilities = {}
        self.initialize_abilities()
        self._haste = min(haste, 0.5)
        self._mana = 100
        self._gcd = 1.5
        self._kills = {}
        self._combat_data = {'hit': 0, 'crit': 0, 'miss': 0, 'dodge': 0}
        self._polling_delay = 0.01

    def reinitialize(self, *, class_name: str = None, abilities: dict = None, haste: float = None, deep: bool = False):
        if class_name:
            self._class = class_name
        if abilities:
            if not are_valid_abilities(abilities):
                raise ValueError("Parameter \'abilities\' must be in the following format: {'1': {'cd': cd1, 'name': name1, 'mana': mana1, 'key': key1}, '2': {'cd': cd2, 'name': name2, 'mana': mana2, 'key': key2}, '3': {'cd': cd3, 'name': name3, 'mana': mana3, 'key': key3}, '4': {'cd': cd4, 'name': name4, 'mana': mana4, 'key': key4}, '5': {'cd': cd5, 'name': name5, 'mana': mana5, 'key': key5}}")
            self._abilities = abilities
            self.initialize_abilities()
        if haste:
            self._haste = min(haste, 0.5)
        if deep:
            self._mana = 100
            self._gcd = 1.5
            self._kills = {}
            self._combat_data = {'hit': 0, 'crit': 0, 'miss': 0, 'dodge': 0}
            self._polling_delay = 0.01

    def initialize_abilities(self):
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
            return self._combat_data.get('crit') / sum(list(self._combat_data.values()))
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

    @property
    def well_defined(self):
        return bool(self._class) and (self._class in CLASS_NAMES)

    def get_kills(self, monster_id):
        return self._kills.get(monster_id)

    def add_combat_data(self, hit_type, n=1):
        try:
            if hit_type != 'none':
                self._combat_data[hit_type] += n
        except KeyError:
            raise ValueError("hit_type must be 'hit', 'crit', 'miss', 'dodge', or 'none'.")

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
        for key in MAIN_ABILITY_KEYS:
            dictionary = copy.deepcopy(self._abilities.get(key))
            if dictionary:
                dictionary.pop('_time')
            string += f'\nAbility-{key}: {dictionary}'
        string += f'\nHaste: {self._haste}\nKills: {self._kills}\nCombat Data: {self._combat_data}'
        return string

    def store(self, force):
        if self._class and self._abilities:
            if not force and CombatKit._new_classes.get(self._class):
                return
            abilities = _del_time(self._abilities)
            CombatKit._new_classes[self._class] = abilities

