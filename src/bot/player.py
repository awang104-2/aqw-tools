from bot.autoclicker import AutoClicker
from game.character import Character
from game.updater import Updater
import toml
import os


def _connection_required(method):
    def wrapper(self, *args, **kwargs):
        if self.__connected.is_clear():
            raise RuntimeError("Call 'connect' before running this method.")
        return method(self, *args, **kwargs)
    return wrapper


class Player:

    _config_path = os.path.join(os.path.dirname(__file__), 'config', 'locations.toml')
    _locations = toml.load(_config_path)
    _clicking = _locations.get('CLICKING')

    ITEM_ACCEPT_LOCATIONS = _clicking['ITEM']['ITEM ACCEPT']
    ITEM_REJECT_LOCATIONS = _clicking['ITEM']['ITEM REJECT']
    QUEST_LOG_LOCATIONS = _clicking['QUEST']['QUEST LOG']
    TURN_IN_LOCATIONS = _clicking['QUEST']['TURN IN']
    NUM_COMPLETE_LOCATIONS = _clicking['QUEST']['NUM COMPLETE']
    YES_LOCATIONS = _clicking['QUEST']['YES']

    def __init__(self, *, resolution=None, server=None):
        self.acc_item_loc = Player.ITEM_ACCEPT_LOCATIONS.get(resolution)
        self.rej_item_loc = Player.ITEM_REJECT_LOCATIONS.get(resolution)
        self.quest_loc = Player.QUEST_LOG_LOCATIONS.get(resolution)
        self.turn_in_loc = Player.TURN_IN_LOCATIONS.get(resolution)
        self.num_loc = Player.NUM_COMPLETE_LOCATIONS.get(resolution)
        self.yes_loc = Player.YES_LOCATIONS.get(resolution)

        self.autoclicker = AutoClicker()
        self.character = Character()
        self.sniffer = GameSniffer(server=server)
        self.interpreter = Updater(character=self.character, sniffer=self.sniffer)

    def connect(self):
        self.sniffer.start()
        self.interpreter.start()

    def disconnect(self):
        self.interpreter.stop()
        self.sniffer.stop()

    def attack(self, key):
        self.autoclicker.press(key)
        self.character.attack(key)

    def wait(self, keys):
        return self.character.wait(keys)

    def print(self):
        print(self.character)

    def save(self):
        self.character.save('all')

