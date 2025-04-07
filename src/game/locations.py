class Location:

    @staticmethod
    def parse_location(location):
        map_name, lobby_num = location.split('-')
        return map_name, lobby_num

    @classmethod
    def load(cls, location):
        map_name, lobby_num = Location.parse_location(location)
        return cls(map_name=map_name, lobby_num=lobby_num)

    def __init__(self, map_name='battleon', lobby_num='1'):
        self._map = map_name.lower()
        self._lobby = lobby_num

    def __str__(self):
        return f'{self._map}-{self._lobby}'

    @property
    def lobby(self):
        return self._lobby

    @property
    def map(self):
        return self._map

    def __self__(self, location):
        self._map, self.lobby_num = Location.parse_location(location)
        return self._map

