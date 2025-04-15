from handlers.ConfigHandler import *
from typing import Self
import math
import time


_config_classes = get_config('classes.toml')
_config_new_classes = get_config('new_classes.toml')

CLASS_ACRONYMS = SafeDict(_config_classes['ACRONYMS'])
CLASS_NAMES = CLASS_ACRONYMS.values()
CLASS_SKILLS = SafeDict(_config_classes['SKILLS'])
NEW_CLASSES = SafeDict(_config_new_classes)
ALL_SKILL_KEYS = ('1', '2', '3', '4', '5', '6')
SPECIAL_SKILL_KEYS = ('2', '3', '4', '5')
MAIN_SKILL_KEYS = ('1', '2', '3', '4', '5')
POTION_KEY = '6'


def _in_string(string, substrings):
    results = []
    for substring in substrings:
        try:
            string.index(substring)
            results.append(True)
        except ValueError:
            results.append(False)
    return results


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
    skills = CLASS_SKILLS.get(class_name, {})
    return class_name, skills


def timeout_condition(t, start_time, timeout):
    if timeout:
        return t - start_time < timeout
    else:
        return True


def _delete_keys(skills, keys):
    skills_copy = copy.deepcopy(skills)
    for skill in skills_copy.values():
        for key in keys:
            del skill[key]
    return skills_copy


def _get_core_info(skills):
    skills_copy = {}
    for skill in skills.values():
        cd, name, mana, key = skill['cd'], skill['name'], skill['mana'], skill['key']
        skills_copy[key] = get_skill(cd, name, mana, key)
    return skills_copy


def get_skill(cd: float, name: str, mana: int, key: str, **kwargs):
    skill = {'cd': cd, 'name': name, 'mana': mana, 'key': key}
    skill.update(kwargs)
    description = kwargs.get('description')
    if description:
        description = description.lower()
        skill['always hits'] = any(_in_string(description, ['can\'t miss', 'always hits']))
        skill['always crits'] = any(_in_string(description, ['can\'t crit', 'always crits']))
    return skill


def _get_skill(cd: float, name: str, mana: int, key: str):
    return {'cd': cd, 'name': name, 'mana': mana, 'key': key, '_time': None}


def valid_skill(skill):
    return skill == get_skill(**skill)


def valid_skills(skills):
    if tuple(skills.keys()) != MAIN_SKILL_KEYS:
        return False
    for skill in skills.values():
        if skill == get_skill(**skill):
            continue
        return False
    return True


def save(config_type):
    new_classes = NEW_CLASSES
    old_classes = _config_classes
    match config_type:
        case 'new':
            write_to_config(new_classes, 'new_classes.toml')
        case 'old':
            write_to_config(old_classes, 'classes.toml')
        case 'both':
            write_to_config(new_classes, 'new_classes.toml')
            write_to_config(old_classes, 'classes.toml')
        case _:
            raise ValueError('config_type must be \'new\', \'old\', or \'both\'.')


def merge(force=False):
    if force:
        CLASS_SKILLS.update(NEW_CLASSES)
    else:
        for class_name, class_skills in NEW_CLASSES.items():
            if class_name not in CLASS_NAMES:
                CLASS_SKILLS[class_name] = class_skills


class InvalidClassError(TypeError):

    def __init__(self, class_name):
        valid_classes = list(CLASS_NAMES)
        string = f'\'{class_name}\' is not a valid class name. Use one from {valid_classes}.'
        super().__init__(string)


class CombatKit:

    @staticmethod
    def save():
        write_to_config(NEW_CLASSES, 'new_classes.toml')

    @classmethod
    def load(cls, class_name=None, haste=0) -> Self:
        skills = None
        if class_name:
            class_name, skills = loads(class_name)
        return CombatKit(class_name, skills=skills, haste=haste)

    def __init__(self, class_name: str | None = None, *, skills: dict | None = None, haste: float = 0):
        self._class = class_name
        self.passives = {}
        if skills:
            self._skills = skills
        else:
            self._skills = {}
        self.initialize_skills()
        self._haste = min(haste, 0.5)
        self._mana = 100
        self._gcd = 1.5
        self._kills = {}
        self._combat_data = {'hit': 0, 'crit': 0, 'miss': 0, 'dodge': 0}
        self._polling_delay = 0.01

    def reinitialize(self, *, class_name: str = None, skills: dict = None, haste: float = None, passives: dict = None, deep: bool = False):
        if class_name:
            self._class = class_name
        if skills:
            if not valid_skills(skills):
                raise ValueError("Parameter \'skills\' must be in the following format: {'1': {'cd': cd1, 'name': name1, 'mana': mana1, 'key': key1}, '2': {'cd': cd2, 'name': name2, 'mana': mana2, 'key': key2}, '3': {'cd': cd3, 'name': name3, 'mana': mana3, 'key': key3}, '4': {'cd': cd4, 'name': name4, 'mana': mana4, 'key': key4}, '5': {'cd': cd5, 'name': name5, 'mana': mana5, 'key': key5}}")
            self._skills = skills
            self.initialize_skills()
        if haste:
            self._haste = min(haste, 0.5)
        if passives:
            self.passives = passives
        if deep:
            self._mana = 100
            self._gcd = 1.5
            self._kills = {}
            self._combat_data = {'hit': 0, 'crit': 0, 'miss': 0, 'dodge': 0}
            self._polling_delay = 0.01

    def initialize_skills(self):
        for skill in self._skills.values():
            skill.update({'_time': None})

    @property
    def name(self):
        return self._class

    @property
    def skills(self):
        return self._skills

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
                skill = self._skills.get(key)
                if skill.get('_time'):
                    time.sleep(self._polling_delay)
                    current_time = time.time()
                    if current_time - skill.get('_time') > self.adjust_for_haste(skill.get('cd')):
                        skill['_time'] = None
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
        skill = self._skills.get(key)
        current_time = time.time()
        if skill is None  :
            raise ValueError('Invalid key.')
        elif skill.get('_time'):
            if current_time - skill.get('_time') > self.adjust_for_haste(skill.get('cd')):
                skill['_time'] = current_time
                self._mana = max(0, self._mana - skill.get('mana'))
            else:
                raise RuntimeError(f'Skill-{key}: \'{skill.get('name')}\' is not ready.')
        else:
            skill['_time'] = current_time
            self._mana = max(0, self._mana - skill.get('mana'))

    def __str__(self):
        string = f'Class Name: {self._class}'
        skills = _get_core_info(self._skills)
        for key, skill in skills.items():
            string += f'\nSkill-{key}: {skill}'
        string += f'\nHaste: {self._haste}\nKills: {self._kills}\nCombat Data: {self._combat_data}'
        return string

    def store(self, force):
        if self._class and self._skills:
            if not force and NEW_CLASSES.get(self._class):
                return
            skills = _delete_keys(self._skills, ['_time'])
            NEW_CLASSES[self._class] = skills

