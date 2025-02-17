from time import sleep
from bot.autoclicker import AutoClicker
from bot.game import Quest, Combat, Inventory, CustomEvent
from packet_logger.sniffer import AqwPacketLogger, Interpreter
from threading import Thread


class Player:

    ITEM_ACCEPT_LOCATIONS = {'2256x1504': (1300, 1150)}
    QUEST_LOG_LOCATIONS = {'2256x1504': [(500, 400)]}
    TURN_IN_LOCATIONS = {'2256x1504': (500, 1100)}
    NUM_COMPLETE_LOCATIONS = {'2256x1504': (1200, 750)}
    YES_LOCATIONS = {'2256x1504': (1050, 800)}

    def __init__(self, resolution, quests):
        self.autoclicker = AutoClicker()
        self.hwnd = self.autoclicker.get_hwnd()
        self.quest = Quest(quests)
        self.combat = Combat(cls='ai')
        self.drops = Inventory()
        self.acc_item_loc = Player.ITEM_ACCEPT_LOCATIONS.get(resolution)
        self.quest_loc = Player.QUEST_LOG_LOCATIONS.get(resolution)
        self.turn_in_loc = Player.TURN_IN_LOCATIONS.get(resolution)
        self.log_on = False

    def add_drop(self, item_id, name, iQty=1):
        quest_reqs = self.quest.get_req_ids()
        return self.drops.add(item_id, name, iQty, quest_reqs)

    def set_inventory(self, item_id, iQtyNow):
        self.drops.set_inventory(item_id, iQtyNow)

    def fight(self):
        move = self.combat.fight()
        if move:
            self.autoclicker.press(move)
            self.combat.sleep_gcd()

    def acc_item(self):
        self.autoclicker.click(self.acc_item_loc)
        sleep(0.5)

    def click_quest(self):
        self.autoclicker.click(self.quest_loc)
        sleep(0.75)

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

    def get_inventory(self):
        return self.drops.get_inventory()


class AdvancedPlayer(Player):

    def __init__(self, resolution, quests, server):
        super().__init__(resolution, quests)
        self.sniffer = AqwPacketLogger(server=server)
        self.fighting = CustomEvent(is_set=False)
        self.pause_fight = CustomEvent(is_set=False)

    def add_drop(self, item_id, name, iQty=1):
        if super().add_drop(item_id, name, iQty):
            self.acc_item()
            turn_ins = self.quest.check_quest(self.drops)
            if any(x > 0 for x in list(turn_ins.values())):
                self.pause_fighting()
                self.toggle_log()
                for ti in list(turn_ins.values):
                    if ti == 0:
                        continue
                    self.click_quest()
                    self.turn_in(ti)
                self.toggle_log()
                self.pause_fighting()

    def start_fighting(self):
        if self.fighting.is_clear():
            self.__combat_loop()

    def stop_fighting(self):
        self.fighting.clear()

    def __combat_loop(self):
        self.fighting.set()
        self.pause_fight.clear()
        while self.is_fighting():
            self.fight()
            self.pause_fight.wait_for_clear()

    def pause_fighting(self):
        if self.pause_fight.is_set():
            self.pause_fight.clear()
        else:
            self.pause_fight.set()

    def change_server(self, server):
        if self.sniffer.is_running():
            raise RuntimeError('Cannot switch servers while logging packets.')
        self.sniffer = AqwPacketLogger(server=server)

    def turn_in_quests(self, n):
        self.toggle_log()
        self.turn_in(n)
        self.toggle_log()

    def is_fighting(self):
        return self.fighting.is_set()


class AutoPlayer(AdvancedPlayer):

    def __init__(self, resolution, quests, server):
        super().__init__(resolution, quests, server)
        self.interpreter = Interpreter(self, self.sniffer)
        self.sniffer.set_concurrent_packet_summary_on(False)
        self.__running = CustomEvent(False)
        self.player_thread = None

    def start_sniff(self):
        self.sniffer.start()

    def start_interpreter(self):
        self.interpreter.start()

    def stop_sniff(self):
        self.sniffer.stop()

    def stop_interpreter(self):
        self.interpreter.stop()

    def run(self):
        self.__running.set()
        self.start_sniff()
        self.start_interpreter()
        self.start_fighting()
        self.stop_sniff()
        self.stop_interpreter()
        self.stop_fighting()
        self.__running.clear()

    def start(self):
        self.player_thread = Thread(target=self.run, daemon=True)
        self.player_thread.start()

    def stop(self):
        self.__running.clear()
        if self.interpreter.is_running():
            self.stop_interpreter()
        if self.sniffer.is_running():
            self.stop_sniff()
        if self.is_fighting():
            self.stop_fighting()

    def is_running(self):
        return self.__running.is_set()



