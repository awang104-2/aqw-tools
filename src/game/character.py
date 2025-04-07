from game.combat import CombatKit


class Character:

    def __init__(self, *, class_name, haste):
        self._combat_kit = CombatKit.load(class_name=class_name, haste=haste)

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
