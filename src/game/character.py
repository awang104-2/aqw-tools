from game.items import Inventory
from game.locations import Location
from game.combat import CombatKit


class Character:

    def __init__(self, class_name=None, *, haste=0, location=None):
        self._combat_kit = CombatKit.load(class_name, haste)
        self._location = Location.load(location)
        self._inventory = Inventory()

    def reinitialize(self, class_name=None, haste=None, location=None):
        if class_name:
            self._combat_kit.reinitialize(class_name)
        if location:
            self._location.update(location)
        if haste:
            self._combat_kit.haste = haste

    @property
    def haste(self):
        return self._combat_kit.haste

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

    def __str__(self):
        return str(self._combat_kit) + '\n' + str(self._location)

