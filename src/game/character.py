from game.combat import CombatKit
from game.items import Item, Inventory
from game.locations import Location
from game.quests import Quest


class Character:

    def __init__(self, *, class_name, haste, quest_names, location=None):
        self._combat = CombatKit.load(class_name=class_name, haste=haste)
        self._quest = Quests.from_names(quest_names)
        self._drops = Inventory()
        self._location = Location(location)

    @property
    def haste(self):
        return self._combat.haste

    @haste.setter
    def haste(self, haste):
        self._combat.haste = haste

    def attack(self, func, *args, **kwargs):
        attack_function = lambda key: func(key, *args, **kwargs)
        self._combat.attack(attack_function)

    def set_inventory(self, item_id, quantity):
        self._drops.set_inventory(item_id, quantity)

    def add_drop(self, item_id, name, quantity=1):
        self._drops.add(item_id, name, quantity)

    def kill(self):
        self._combat.add_kills(n=1)

    def add_combat_data(self, data):
        self._combat.add_combat_data()

