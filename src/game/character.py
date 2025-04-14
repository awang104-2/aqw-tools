from game.items import Inventory
from game.locations import Location
from game.combat import Class
from handlers.DataHandler import add_to_csv
import os


project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
datapath = os.path.join(project_root, 'data', 'crit_chance_data.csv')


class Character:

    def __init__(self):
        self.cls = Class()
        self.location = Location()
        self.inventory = Inventory()

    def __str__(self):
        string = f'{self.get_class_name()}\n'
        string += self.get_skills_as_str()
        return string

    def get_class_name(self):
        return self.cls.name

    def get_skills_as_str(self):
        string = ''
        for ref, skill in self.cls.skills.items():
            string += f'{skill}\n'
        return string

    @property
    def map(self):
        return self.location.map

    def lobby(self, anonymize=False):
        lobby = self.location.lobby
        if anonymize:
            lobby = 'xxxxx'
        return lobby

    def get_location(self, anonymize=False):
        lobby = self.location.lobby
        if anonymize:
            lobby = 'xxxxx'
        return f'{self.location.map}-{lobby}'

    def total_data(self):
        data = {'hit': 0, 'miss': 0, 'dodge': 0, 'crit': 0}
        for skill in self.cls.skills.values():
            for key, value in skill.data.items():
                data[key] += value
        return data

    def total_data_as_str(self):
        data = self.total_data()
        total = 0
        for value in data.values():
            total += value
        return f'Hits: {data['hit']} | Misses: {data['miss']} | Dodges: {data['dodge']} | Crits {data['crit']} | Total {total}'

    def crit_data(self):
        data = {'crit': 0, 'total': 0}
        for skill in self.cls.skills.values():
            if skill.force != 'crit' and skill.force != 'hit':
                data['crit'] += skill.data['crit']
                data['total'] += skill.total()
        return data

    def save(self):
        data = self.crit_data()
        upload_data = {}
        for key, value in data.items():
            upload_data[key] = [value]
        upload_data['class'] = self.cls.name
        if data['total'] > 0:
            upload_data['chance'] = [round(data['crit'] / data['total'], 5)]
        else:
            upload_data['chance'] = [0]
        print(upload_data)
        add_to_csv(datapath, upload_data)



'''
class Character:

    @staticmethod
    def create_skill(cd: float, name: str, mana: int, key: str, **kwargs):
        return get_skill(cd, name, mana, key, **kwargs)

    def __init__(self, class_name=None, *, haste=0, location=None):
        self._combat_kit = Class.load(class_name, haste)
        self._location = Location.load(location, False)
        self._inventory = Inventory()

    def reinitialize(self, *, class_name=None, skills=None, passives=None, haste=None, location=None, monsters=None):
        if class_name or skills or passives or haste:
            self._combat_kit.reinitialize(class_name=class_name, skills=skills, passives=passives, haste=haste)
        if location or monsters:
            self._location.update(location, monsters)

    @property
    def map(self):
        return self._location.map

    def lobby(self, anonymize=False):
        lobby = self._location.lobby
        if anonymize:
            lobby = 'xxxxx'
        return lobby

    def location(self, anonymize=False):
        lobby = self._location.lobby
        if anonymize:
            lobby = 'xxxxx'
        return f'{self._location.map}-{lobby}'

    def _get_attribute(self, attribute):
        match attribute:
            case 'hits':
                return self._combat_kit.hits
            case 'misses':
                return self._combat_kit.misses
            case 'dodges':
                return self._combat_kit.dodges
            case 'crits':
                return self._combat_kit.crits
            case 'total':
                return self._combat_kit.total
            case 'kills':
                return self._combat_kit.kills
            case _:
                raise ValueError('Unimplemented or invalid attribute.')

    def get(self, attribute):
        return self._get_attribute(attribute)

    def get_many(self, attributes):
        result = {}
        for attribute in attributes:
            result[attribute] = self._get_attribute(attribute)
        return result

    @property
    def map(self):
        return self._location.map

    def lobby(self, anonymize=False):
        lobby = self._location.lobby
        if anonymize:
            lobby = 'xxxxxxxxx'
        return lobby

    def location(self, anonymize=False):
        lobby = self._location.lobby
        if anonymize:
            lobby = 'xxxxxxxxx'
        return f'{self._location.map}-{lobby}'

    @property
    def map(self):
        return self._location.map

    def lobby(self, anonymize=False):
        lobby = self._location.lobby
        if anonymize:
            lobby = 'xxxxxxxxx'
        return lobby

    def location(self, anonymize=False):
        lobby = self._location.lobby
        if anonymize:
            lobby = 'xxxxxxxxx'
        return f'{self._location.map}-{lobby}'

    @property
    def map(self):
        return self._location.map

    def lobby(self, anonymize=False):
        lobby = self._location.lobby
        if anonymize:
            lobby = 'xxxxxxxxx'
        return lobby

    def location(self, anonymize=False):
        lobby = self._location.lobby
        if anonymize:
            lobby = 'xxxxxxxxx'
        return f'{self._location.map}-{lobby}'

    @property
    def haste(self):
        return self._combat_kit.haste

    @property
    def class_name(self):
        return self._combat_kit.name

    @haste.setter
    def haste(self, haste):
        self._combat_kit.haste = haste

    def attack(self, key):
        self._combat_kit.attack(key)
        self._combat_kit.sleep_gcd()

    def wait(self, keys):
        return self._combat_kit.wait(keys)

    def add(self, item_id, name, quantity):
        self._inventory.add(item_id, name, quantity)

    def kill(self, local_id):
        monster_id = self._location.map + ':' + str(local_id)
        self._combat_kit.add_kills(monster_id, 1)

    def add_combat_data(self, hit_type):
        self._combat_kit.add_combat_data(hit_type)

    def is_class_defined(self):
        return self._combat_kit.well_defined

    def __str__(self):
        return f'{str(self._combat_kit)}\n{str(self._location)}'

    def store(self, attribute):
        match attribute:
            case 'combat kit':
                self._combat_kit.store(False)
            case 'location':
                self._location.store(force=True)
            case 'all':
                self._combat_kit.store(False)
                self._location.store(True)
            case _:
                raise ValueError('attribute must be \'combat kit\', \'location\', or \'all\'.')

    def save(self, attribute):
        match attribute:
            case 'combat kit':
                self._combat_kit.save()
            case 'location':
                self._location.save()
            case 'all':
                self._combat_kit.save()
                self._location.save()
            case _:
                raise ValueError('attribute must be \'combat kit\', \'location\', or \'all\'.')
'''

__all__ = [name for name in globals() if not name.startswith('-')]
