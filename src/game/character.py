from game.items import Inventory
from game.locations import Location
from game.combat import CombatKit, get_ability


class Character:

    @staticmethod
    def create_ability(cd: float, name: str, mana: int, key: str):
        return get_ability(cd, name, mana, key)

    def __init__(self, class_name=None, *, haste=0, location=None):
        self._combat_kit = CombatKit.load(class_name, haste)
        self._location = Location.load(location, False)
        self._inventory = Inventory()

    def reinitialize(self, *, class_name=None, abilities=None, haste=None, location=None, monsters=None):
        if class_name:
            self._combat_kit.reinitialize(class_name=class_name)
        if abilities:
            self._combat_kit.reinitialize(abilities=abilities)
        if location or monsters:
            self._location.update(location, monsters)
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

    def is_class_defined(self):
        return self._combat_kit.well_defined

    def __str__(self):
        return f'{str(self._combat_kit)}\n{str(self._location)}'

    def store(self, attribute):
        match attribute:
            case 'combat kit':
                self._combat_kit.store(True)
            case 'location':
                self._location.store(force=True)
            case 'all':
                self._combat_kit.store(True)
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


__all__ = [name for name in globals() if not name.startswith('-')]
