from game.combat import CombatKit
from game.locations import Location


class Character:

    def __init__(self, *, class_name=None, haste=None, location=None):
        if class_name and haste:
            self._combat_kit = CombatKit.load(class_name=class_name, haste=haste)
        else:
            self._combat_kit = None
        if location:
            self._location = Location(location)
        else:
            self._location = None

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

    def initialize(self, class_name=None, haste=None, location=None):
        if class_name and haste:
            self._combat_kit = CombatKit.load(class_name=class_name, haste=haste)
        else:
            self._combat_kit = None
        if location:
            self._location = Location(location)
        else:
            self._location = None
