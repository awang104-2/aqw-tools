from handlers.DictHandler import *
import toml
import os


class Quest:

    _config_path = os.path.join(os.path.dirname(__file__), 'config', 'quests.toml')
    _quest_config = toml.load(_config_path)

    def __init__(self, name, requirements, cap):
        self.name = name.upper()
        self.requirements = deepcopy(requirements)
        self.cap = deepcopy(cap)
        self.progress = dict.fromkeys(self.requirements, 0)
        self.num_completed = 0

    @classmethod
    def load(cls, name):
        quest_details = Quest._quest_config.get(name)
        name = name.upper()
        requirements = quest_details.get('REQUIREMENTS')
        cap = quest_details.get('CAP')
        return cls(name=name, requirements=requirements, cap=cap)

    def get_item_ids(self):
        return list(self.requirements.keys())

    def is_required_item(self, item_id):
        return item_id in self.get_item_ids()

    def add(self, item_id, number):
        self.progress[item_id] += number

    def print(self):
        print(f'{self.name}')
        for item_id, num in self.progress.items():
            print(f'{item_id}: {num}')

    def check_quest(self):
        quests_satisfied = 0
        for item_id, condition in self.requirements.items():
            condition_satisfied = int(self.progress.get(item_id) / condition)
            if condition_satisfied < quests_satisfied:
                quests_satisfied = condition_satisfied
        return quests_satisfied

    def complete(self, n):
        for item_id in self.progress.keys():
            self.progress[item_id] -= n * self.requirements.get(item_id)
            if self.progress.get(item_id) < 0:
                raise ValueError('Argument \'n\' is too large, not enough quests completed.')
        self.num_completed += n

    def copy(self):
        return Quest(name=self.name, requirements=self.requirements, cap=self.cap)