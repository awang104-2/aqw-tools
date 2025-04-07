import toml
import os


class Item:

    _config_path = os.path.join(os.path.dirname(__file__), 'config', 'drops.toml')


class Inventory:

    _config_path = os.path.join(os.path.dirname(__file__), 'config', 'drops.toml')
    _sampling_path = os.path.join(os.path.dirname(__file__), 'config', 'sampling.toml')

    @staticmethod
    def get_db():
        with open(Inventory._config_path, 'r') as file:
            drop_config = toml.load(file)
        return drop_config

    @staticmethod
    def write_db(db):
        with open(Inventory._config_path, 'w') as file:
            toml.dump(db, file)

    def __init__(self):
        self.inventory = {}
        self.drops = {}

    def __str__(self):
        return f'Drops: {self.drops}\nInventory: {self.inventory}'

    def set_inventory(self, item_id, iQtyNow):
        self.inventory[item_id]['count'] = iQtyNow

    def add(self, item_id, name, iQty):
        if self.drops.get(item_id, False):
            self.drops[item_id]['count'] += iQty
            self.inventory[item_id]['count'] += iQty
        else:
            self.drops[item_id] = {'name': name, 'count': iQty}
            self.inventory[item_id] = {'name': name, 'count': iQty}
        if not self.drops.get(item_id).get('name'):
            self.drops[item_id]['name'] = name
            self.inventory[item_id]['name'] = name

    def subtract(self, item_id, iQty):
        self.drops[item_id] -= iQty

    def get_drops(self):
        return self.drops.copy()

    def get_drop(self, item_id):
        return self.drops.get(item_id, None)

    def get_inventory(self):
        return self.inventory.copy()

    def reset(self):
        for key in self.inventory.keys():
            self.inventory[key]['count'] = 0
        for key in self.drops.keys():
            self.drops[key]['count'] = 0

    def save(self, filepath=None):
        if not filepath:
            filepath = Inventory._sampling_path
        drops = self.get_drops()
        for item_id in drops.keys():
            if not drops.get(item_id).get('name'):
                drops[item_id]['name'] = 'None'
        with open(filepath, 'w') as file:
            toml.dump(drops, file)

    def merge_db(self, filepath=None):
        db = self.get_db()
        if not filepath:
            filepath = Inventory._sampling_path
        with open(filepath, 'r') as file:
            data = toml.load(file)
        for key, value in data.items():
            if value.get('name') != 'None' and db.get(key) and db.get(key).get('name') == 'None':
                db[key]['name'] = value.get('name')
            elif not db.get(key):
                db[key] = {'name': value.get('name')}
        self.write_db(db)
