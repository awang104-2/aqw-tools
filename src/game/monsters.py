from handlers.ConfigHandler import SafeDict, get_config


_config = get_config('monsters.toml')
MONSTERS = SafeDict(_config)


class ExclusiveArgumentError(ValueError):

    def __init__(self, msg):
        super().__init__(msg)


class NoArgumentError(ValueError):

    def __init__(self, msg):
        super().__init__(msg)


class Unimplemented(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class Monster:

    @classmethod
    def load(cls, *, name=None, monster_id=None):
        if name and monster_id:
            raise ExclusiveArgumentError('Either provide name or monster_id, not both.')
        elif not (name or monster_id):
            raise NoArgumentError('Must provide an argument.')
        elif name:
            return cls(**MONSTERS.get(name, name))
        elif monster_id:
            raise Unimplemented('monster_id unimplemented.')

    def __init__(self, name, race=None, monster_id=None, map_id=None, total_hp=None):
        self.name = name
        self.race = race
        self.monster_id = monster_id
        self.map_id = map_id
        self.total_hp = total_hp

    @property
    def local_id(self):
        return self.map_id.split(':')[-1]


__all__ = [name for name in globals() if not name.startswith('-')]

