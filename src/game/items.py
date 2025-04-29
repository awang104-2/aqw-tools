from handlers.ConfigHandler import *
import toml


_config_path = get_config_path('drops.toml')
_config = get_config('drops.toml')
ITEM_INFO = SafeDict(_config)


class Item:

    def __init__(self, item_id: str | int, count: int, *, name: str = None, level: int = None, cap: int = None, description: str = None, **kwargs):
        self.item_id = str(item_id)
        self.name = name
        self.level = level
        self.cap = cap
        self.description = description
        self.count = count
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return f'Item ID: {self.item_id} | Name: {self.name} | Count: {self.count}'

    def __eq__(self, other):
        equals = True
        if self.name and other.name:
            equals = equals and self.name == other.name
        if self.item_id and other.item_id:
            equals = equals and self.item_id == other.item_id
        if self.level and other.level:
            equals = equals and self.level == other.level
        if self.cap and other.cap:
            equals = equals and self.cap == other.cap
        if self.description and other.description:
            equals = equals and self.description == other.descriptioin
        return equals

    def add(self, *, n=None, other=None):
        if n:
            self.count += n
        if other:
            self.count += other.count
        if self.cap:
            self.count = min(self.count, self.cap)

    def __add__(self, other):
        new_item = self.copy()
        new_item.add(other=other)
        return new_item

    def __iadd__(self, other):
        if self != other:
            raise ValueError('Must be the same kind of items.')
        new_item = self + other
        return new_item

    def to_dict(self):
        return vars(self)

    def store(self):
        dictionary = {self.item_id: {'name': self.name, 'level': self.level, 'cap': self.cap, 'description': self.description}}
        ITEM_INFO.update(dictionary)

    def copy(self):
        return Item(**vars(self))


class Inventory:

    def __init__(self, *items):
        self.drops = {}
        for item in items:
            item_id = item.item_id
            if self.drops.get(item_id):
                self.drops.get(item_id).add(other=item)
            else:
                self.drops[item_id] = item

    def __str__(self):
        string = ''
        for drop in self.drops.values():
            if drop.name:
                string += f'{drop.name}: {drop.count} | '
            else:
                string += f'{drop.item_id}: {drop.count} | '
        return string[:-3]

    def add(self, other):
        item = self.drops.get(other.item_id)
        if item:
            item += other
        else:
            self.drops[other.item_id] = other

    def reset(self):
        for item in self.drops.values():
            item.count = 0

    def save(self):
        for item_id in self.drops.keys():
            if not self.drops.get(item_id).get('name'):
                self.drops[item_id]['name'] = 'Unknown'
        write_to_file(self.drops, _config_path)


__all__ = [name for name in globals() if not name.startswith('-')]

