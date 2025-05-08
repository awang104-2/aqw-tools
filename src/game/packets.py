from abc import ABC, abstractmethod
from game.combat import Skill, Passive, Class
from game.locations import Location
from handlers.ConfigHandler import SafeDict, get_config
from network.sniffing import JsonSniffer
import types


_config = get_config('backend.toml')
PACKETS = {}


def update_character(json, character):
    cmd = json['cmd']
    packet_type = PACKETS.get(cmd)
    if packet_type:
        update_packet = packet_type(json)
        update_packet.update(character)


class PacketConstructionError(Exception):

    def __init__(self, msg):
        super().__init__(msg)


class GamePacket(ABC):

    cmd = None
    msg = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.cmd:
            raise NotImplementedError(f'{cls.__name__} must define \'cmd\'.')
        if not cls.msg:
            raise NotImplementedError(f'{cls.__name__} must define \'msg\'.')
        PACKETS[cls.cmd] = cls

    @abstractmethod
    def update(self, character):
        pass


class ClassPacket(GamePacket):

    cmd = 'updateClass'
    msg = 'Updated class skills and passives.'

    @staticmethod
    def from_host(json):
        return bool(json.get('sDesc'))

    def __init__(self, json: dict):
        super().__init__()
        self.name = json.get('sClassName')
        self.description = json.get('sDesc')

    def for_user(self):
        return self.name and self.description

    def update(self, character):
        if self.for_user():
            character.cls = Class(name=self.name, description=self.description)


class SkillsPacket(GamePacket):

    cmd = 'sAct'
    msg = 'Updated class name and description.'

    def __init__(self, json: dict):
        super().__init__()
        self.skills = json['actions']['active'][:5]
        self.passives = json['actions']['passive']

    @property
    def num_skills(self):
        return len(self.skills)

    @property
    def num_passives(self):
        return len(self.passives)

    def get_skill_attributes(self, i):
        skill = self.skills[i]
        return {
            'name': skill['nam'],
            'mp': skill['mp'],
            'cd': skill['cd'] / 1000,
            'reference': skill['ref'],
            'force': skill.get('forceResult'),
            'description': skill['desc'].replace('’', "'"),
            'damage': skill.get('damage'),
            'targets': [skill.get('tgtMin'), skill.get('tgtMax')]
        }

    def get_passive_attributes(self, i):
        passive = self.skills[i]
        return {
            'name': passive['nam'],
            'description': passive['desc'].replace('’', "'")
        }

    def update(self, character):
        skills = []
        for i in range(self.num_skills):
            attributes = self.get_skill_attributes(i)
            skills.append(Skill(**attributes))
        passives = []
        for i in range(self.num_passives):
            attributes = self.get_passive_attributes(i)
            passives.append(Passive(**attributes))
        character.cls.update(skills=skills, passives=passives)


class LocationPacket(GamePacket):

    cmd = 'moveToArea'
    msg = 'Updated location.'

    def __init__(self, json: dict):
        super().__init__()
        self.location = json.get('areaName')

    def update(self, character):
        character.location = Location.load(self.location)


class InventoryPacket(GamePacket):

    cmd = 'loadInventoryBig'
    msg = 'Updated inventory.'

    def __init__(self, json):
        super().__init__()
        self.items = json['items']
        self.bank = json['bankCount']

    def update(self, character):
        pass


class CombatPacket(GamePacket):

    cmd = 'ct'
    msg = 'Updated combat info.'

    ALWAYS_HIT = 'noMiss'
    NEVER_MISS = 'noMiss'
    ALWAYS_CRIT = 'crit'

    def __init__(self, json):
        super().__init__()
        self.combat_data = None
        keys = json.keys()
        if 'sarsa' in keys:
            self.combat_data = json['sarsa']

    def update(self, character):
        for sarsa in self.combat_data:
            datapoints = sarsa['a']
            for datapoint in datapoints:
                reference = datapoint.get('actRef')
                attack_type = datapoint.get('type')
                skill = character.cls.get_skill(reference)
                skill.register(attack_type)


AQW_SERVERS = SafeDict(_config['AQW']['SERVERS'])
AQW_PACKETS = SafeDict(_config['AQW']['PACKETS'])
AQW_SERVER_NAMES = list(AQW_SERVERS.keys())
AQW_SERVER_IPS = list(AQW_SERVERS.values())


class GameSniffer(JsonSniffer):

    def __init__(self, server, *, daemon=False):
        server_filter = ''
        if server == 'any' or server == 'all':
            for ip in AQW_SERVER_IPS:
                server_filter += f'src host {ip} or '
            server_filter = server_filter[:-4]
        elif server in AQW_SERVER_NAMES or server in AQW_SERVER_IPS:
            server = AQW_SERVERS.get(server, server).lower()
            server_filter = f'src host {server}'
        else:
            raise ValueError('Not a valid server.')
        bpf_filter = f'tcp and ({server_filter})'
        super().__init__(bpf_filter=bpf_filter, daemon=daemon)
        self.server = server


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]