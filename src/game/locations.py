from handlers.ConfigHandler import *


_config = get_config('locations.toml')
LOCATIONS = SafeDict(_config)


class Location:

    @staticmethod
    def parse_location(location):
        map_name, lobby_num = location.split('-')
        return map_name.lower(), int(lobby_num)

    @classmethod
    def load(cls, location, with_lobby):
        if location:
            if with_lobby:
                map_name, lobby_num = Location.parse_location(location)
            else:
                map_name, lobby_num = location, None
            monsters = LOCATIONS.get(map_name)
            if monsters:
                monsters = LOCATIONS.get(map_name)
            return cls(map_name, lobby_num, monsters)
        else:
            return cls()

    def __init__(self, map_name: str = None, lobby_num: int = None, monsters: dict = None):
        self.map = map_name
        if self.map:
            self.map.lower()
        self.lobby = lobby_num
        if not monsters:
            monsters = {}
        self.monsters = monsters

    def update(self, location=None, monsters=None):
        if location:
            self.map, self.lobby = Location.parse_location(location)
        if monsters:
            self.monsters = monsters

    def __str__(self):
        return f'Location: {self.map}-{self.lobby}'

    def __repr__(self):
        return f'{self.map}-{self.lobby}'

    def add(self, monster):
        self.monsters[monster.local_id] = monster.name

    def to_dict(self):
        return {self.map: self.monsters}

    def store(self, force):
        if not force and LOCATIONS.get(self.map):
            return
        dictionary = self.to_dict()
        LOCATIONS.update(dictionary)

    def save(self):
        write_to_config(LOCATIONS, 'locations.toml')








