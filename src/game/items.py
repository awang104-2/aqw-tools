from handlers.ConfigHandler import *
import toml


_config_path = get_config_path('drops.toml')
_config = get_config('drops.toml')
ITEM_INFO = SafeDict(_config)


class Inventory:

    def __init__(self, sampling_path=None):
        self.inventory = {}
        self.drops = {}
        if sampling_path:
            self.sampling_path = sampling_path
        else:
            self.sampling_path = get_config_path('sampling.toml')

    def __str__(self):
        return f'Drops: {self.drops}\nInventory: {self.inventory}'

    def set_inventory(self, item_id, inventory_quantity):
        self.inventory[item_id]['count'] = inventory_quantity

    def add(self, item_id, name, quantity):
        if isinstance(item_id, int):
            item_id = str(item_id)
        drops = self.drops.get(item_id)
        inventory = self.inventory.get(item_id)
        if not name:
            name = ITEM_INFO.get(item_id)
        if drops:
            drops['count'] += quantity
            inventory['count'] += quantity
            if not drops.get('name') and name:
                drops['name'] = name
        else:
            self.drops[item_id] = {'name': name, 'count': quantity}
            self.inventory[item_id] = {'name': name, 'count': quantity}

    def subtract(self, item_id, quantity):
        self.drops[item_id] -= quantity

    def reset(self):
        for key in self.inventory.keys():
            self.inventory[key]['count'] = 0
        for key in self.drops.keys():
            self.drops[key]['count'] = 0

    def save(self):
        for item_id in self.drops.keys():
            if not self.drops.get(item_id).get('name'):
                self.drops[item_id]['name'] = 'Unknown'
        write_to_file(self.drops, self.sampling_path)

    def merge_config(self):
        sample = toml.load(self.sampling_path)
        for item in sample.values():
            item.pop('count')
        ITEM_INFO.update(sample)
        write_to_config(ITEM_INFO, 'drops.toml')


__all__ = [name for name in globals() if not name.startswith('-')]


