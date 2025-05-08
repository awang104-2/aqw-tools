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


class InvalidClassError(TypeError):

    def __init__(self, class_name):
        valid_classes = list(CLASS_NAMES)
        string = f'\'{class_name}\' is not a valid class name. Use one from {valid_classes}.'
        super().__init__(string)


class Passive:

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return f'{self.name}: {self.description}'


class Skill:

    def __init__(self, *, name, mp, cd, reference, force=None, description=None, damage=None, targets=None, **kwargs):
        self.name = name
        self.mp = mp
        self.cd = cd
        self.reference = reference
        self.force = force
        self.description = description
        self.damage = damage
        self.data = {'hit': 0, 'crit': 0, 'miss': 0, 'dodge': 0}
        self.targets = targets
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def key(self):
        match self.reference:
            case 'aa':
                return '1'
            case 'a1':
                return '2'
            case 'a2':
                return '3'
            case 'a3':
                return '4'
            case 'a4':
                return '5'

    def __str__(self):
        return f'Name: {self.name} | MP: {self.mp} | CD: {self.cd}'

    def to_dict(self):
        return {'name': self.name, 'cd': self.cd, 'mp': self.mp, 'key': self.key, 'force result': self.force}

    def total(self):
        values = list(self.data.values())
        return sum(values)

    def register(self, attk_type):
        if attk_type in self.data.keys():
            self.data[attk_type] += 1

    def get_core_info(self):
        return {'name': self.name, 'mp': self.mp, 'cd': self.cd, 'force': self.force, 'key': self.key}


class Stats:

    def __init__(self, haste=None, hp=None, mp=None, gcd=1.5):
        self.haste = min(haste, 0.5)
        self.hp = hp
        self.mp = mp
        self.gcd = gcd

    def update(self, haste=None, hp=None, mp=None, gcd=None):
        if haste:
            self.haste = haste
        if hp:
            self.hp = hp
        if mp:
            self.mp = mp
        if gcd:
            self.gcd = gcd

    @property
    def cd_reduction(self):
        return 1 - self.haste


class Class:

    def __init__(self, name='No Class', description=None, skills: dict = None, passives: list = None):
        if not skills:
            skills = {}
        if not passives:
            passives = {}
        self.name = name
        self.description = description
        self.skills = skills
        self.passives = passives

    def get_skill(self, reference):
        return self.skills.get(reference)

    def get_passive(self, i):
        try:
            return self.passives[i]
        except IndexError:
            return None

    def defined(self):
        return self.name and self.skills

    def add_skill(self, skill):
        key = skill.reference
        self.skills[key] = skill

    def update(self, name=None, skills=(), passives=()):
        if name:
            self.name = name
        if skills:
            for skill in skills:
                self.add_skill(skill)

    def store(self, force=False):
        if force:
            NEW_CLASSES.update({self.name: self.skills})
        else:
            if not NEW_CLASSES.get(self.name):
                NEW_CLASSES.update({self.name: self.skills})


'''
class CombatKit:

    def __init__(self, name: str = None, *, skills: dict | None = None, haste: float = 0):
        self._class = name
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
            self._combat_data = {'hit': 0, 'crit': 0, 'miss': 0, 'dodge': 0, 'force hit': 0, 'force crit': 0, 'never miss': 0}
            self._polling_delay = 0.01

    def initialize_skills(self):
        for skill in self._skills.values():
            skill.update({'_time': None})

    @property
    def hits(self):
        return self._combat_data['hit']

    @property
    def dodges(self):
        return self._combat_data['dodge']

    @property
    def crits(self):
        return self._combat_data['crit']

    @property
    def misses(self):
        return self._combat_data['miss']

    @property
    def total(self):
        return self._combat_data['hit'] + self._combat_data['dodge'] + self._combat_data['crit'] + self._combat_data['miss']

    @property
    def kills(self):
        return copy.deepcopy(self._kills)

    @property
    def name(self):
        return self._class

    @property
    def skills(self):
        return self._skills

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
'''