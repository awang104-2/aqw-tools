from time import sleep
from bot.autoclicker import AutoClicker
from bot.game import Quest, Combat, Drops
from packet_logger.sniffer import AqwPacketLogger


class Player:

    item_accept_locations = {'2256x1504': (1300, 1150)}

    def __init__(self):
        self.autoclicker = AutoClicker()
        self.hwnd = self.autoclicker.get_hwnd()
        self.quest = Quest(resolution='2256x1504')
        self.combat = Combat(cls='ai')
        self.drops = Drops(resolution='2256x1504')
        self.sniffer = AqwPacketLogger(server='twig')

    def fight(self):
        pass

    def collect_item(self, packet):
        loc = self.drops.add(packet)
        self.autoclicker.click(loc)
        sleep(0.2)

    def toggle_log(self):
        self.autoclicker.press('l')
        sleep(0.75)

