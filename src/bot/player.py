from time import sleep
from bot.autoclicker import AutoClicker
from bot.game import Quest, Combat, Drops, CustomEvent
from packet_logger.sniffer import AqwPacketLogger


class Player:

    ITEM_ACCEPT_LOCATIONS = {'2256x1504': (1300, 1150)}
    QUEST_LOG_LOCATIONS = {'2256x1504': [(500, 400)]}
    TURN_IN_LOCATIONS = {'2256x1504': (500, 1100)}
    NUM_COMPLETE_LOCATIONS = {'2256x1504': (1200, 750)}
    YES_LOCATIONS = {'2256x1504': (1050, 800)}

    def __init__(self, resolution, quest):
        self.autoclicker = AutoClicker()
        self.hwnd = self.autoclicker.get_hwnd()
        self.quest = Quest(quest)
        self.combat = Combat(cls='ai')
        self.drops = Drops()
        self.sniffer = AqwPacketLogger(server='twig')
        self.acc_item_loc = Player.ITEM_ACCEPT_LOCATIONS.get(resolution)
        self.quest_loc = Player.QUEST_LOG_LOCATIONS.get(resolution)
        self.turn_in_loc = Player.TURN_IN_LOCATIONS.get(resolution)
        self.log_on = False

    def fight(self):
        move = self.combat.fight()
        if move:
            self.autoclicker.press(move)
            self.combat.sleep_gcd()

    def acc_item(self):
        self.autoclicker.click(self.acc_item_loc)
        sleep(0.2)

    def turn_in(self, n):
        self.quest.turn_in(self.drops, n)
        self.autoclicker.click(self.turn_in_loc)
        sleep(0.75)

    def toggle_log(self):
        self.log_on = not self.log_on
        self.autoclicker.press('l')
        sleep(0.75)

    def get_total_kills(self):
        return self.combat.get_kills()

    def get_drops(self):
        return self.drops.get_drops()


class AdvancedPlayer(Player):

    def __init__(self, resolution, quest):
        super().__init__(resolution, quest)
        self.fighting = CustomEvent(is_set=False)

    def fight_continuously(self):
        if self.fighting.is_clear():
            self.__combat_loop()

    def stop_fighting(self):
        self.fighting.clear()

    def __combat_loop(self):
        self.fighting.set()
        while self.fighting.is_set():
            self.fight()

    def turn_in_quests(self, n):
        self.toggle_log()
        self.turn_in(n)
        self.toggle_log()


class AutoPlayer(AdvancedPlayer):

    def __init__(self, resolution, quest, server):
        super().__init__(resolution, quest)
        self.logger = AqwPacketLogger(server)
        self.running = CustomEvent(False)

    def run(self):
        self.running.set()
        self.logger.start()
        self.fight_continuously()

    def stop(self, print_logs=False):
        self.stop_fighting()
        self.logger.stop()
        if print_logs:
            self.logger.print_packets_as_data()

