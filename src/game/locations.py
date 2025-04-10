class Location:

    @staticmethod
    def parse_location(location):
        map_name, lobby_num = location.split('-')
        return map_name.lower(), int(lobby_num)

    @classmethod
    def load(cls, location):
        if location:
            map_name, lobby_num = Location.parse_location(location)
            return cls(map_name, lobby_num)
        else:
            return cls()

    def __init__(self, map_name: str = None, lobby_num: int = None):
        self._map = map_name
        if self._map:
            self._map.lower()
        self._lobby = lobby_num

    @property
    def lobby(self):
        return self._lobby

    @property
    def map(self):
        return self._map

    def update(self, location):
        self._map, self._lobby = Location.parse_location(location)

    def __str__(self):
        return f'Location: {self._map}-{self._lobby}'

    def __repr__(self):
        return f'{self._map}-{self._lobby}'



