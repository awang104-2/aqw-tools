from game.items import Inventory
from game.locations import Location
from game.combat import Class
from handlers.DataHandler import add_to_csv
import os


project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
datapath = os.path.join(project_root, 'data', 'crit_chance_data.csv')


def unit_notation(integer):
    if integer < 1000:
        return str(integer)
    elif integer < 1000000:
        integer = int(integer / 100) / 10
        return str(integer) + 'k'
    else:
        integer = int(integer / 1000 / 100) / 10
        return str(integer) + 'm'


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
        return f'Hits: {unit_notation(data['hit'])} | Misses: {unit_notation(data['miss'])} | Dodges: {unit_notation(data['dodge'])} | Crits {unit_notation(data['crit'])} | Total {unit_notation(total)}'

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


__all__ = [name for name in globals() if not name.startswith('-')]
