from time import sleep, time
from bot.autoclicker import AutoClicker
from bot.game import Quest, Combat, Inventory, CustomEvent
from packet_logger.sniffer import AqwPacketLogger, Interpreter
from threading import Thread


class Player:

    ITEM_ACCEPT_LOCATIONS = {'2256x1504': (1300, 1150)}
    ITEM_REJECT_LOCATIONS = {'2256x1504': (1350, 1150)}
    QUEST_LOG_LOCATIONS = {'2256x1504': (500, 400)}
    TURN_IN_LOCATIONS = {'2256x1504': (500, 1100)}
    NUM_COMPLETE_LOCATIONS = {'2256x1504': (1140, 680)}
    YES_LOCATIONS = {'2256x1504': (1050, 800)}

    def __init__(self, resolution, quests, location='battleon', haste=0.5, cls='lr'):
        self.resolution = resolution
        self.autoclicker = AutoClicker()
        self.hwnd = self.autoclicker.get_hwnd()
        self.location = location
        self.quest = Quest(quests)
        self.combat = Combat(cls=cls, haste=haste)
        self.drops = Inventory()
        self.acc_item_loc = Player.ITEM_ACCEPT_LOCATIONS.get(self.resolution)
        self.rej_item_loc= Player.ITEM_REJECT_LOCATIONS.get(self.resolution)
        self.quest_loc = Player.QUEST_LOG_LOCATIONS.get(self.resolution)
        self.turn_in_loc = Player.TURN_IN_LOCATIONS.get(self.resolution)
        self.num_loc = Player.NUM_COMPLETE_LOCATIONS.get(self.resolution)
        self.yes_loc = Player.YES_LOCATIONS.get(self.resolution)
        self.log_on = False
        self.timelapse = {'1': time(), '2': time(), '3': time(), '4': time(), '5': time(), 'gcd': time()}
        self.delay_time = 0.1

    def add_drop(self, item_id, name, iQty=1, is_drop=False):
        quest_reqs = self.quest.get_req_ids()
        return self.drops.add(item_id, name, iQty, quest_reqs)

    def set_inventory(self, item_id, iQtyNow):
        self.drops.set_inventory(item_id, iQtyNow)

    def delay(self):
        sleep(self.delay_time)

    def fight(self):
        move = self.combat.fight()
        if move:
            self.autoclicker.press(move)
            self.timelapse[move] = time()
            self.timelapse['gcd'] = time()
            self.combat.sleep_gcd()
        else:
            self.delay()

    def acc_item(self):
        self.autoclicker.click(self.acc_item_loc)
        sleep(0.25)

    def rej_item(self):
        self.autoclicker.click(self.rej_item_loc)
        sleep(0.25)

    def click_quest(self):
        self.autoclicker.click(self.quest_loc)
        sleep(0.5)

    def turn_in(self, n):
        self.autoclicker.click(self.turn_in_loc)
        if n > 1:
            self.input_quest_num()
        sleep(0.75)

    def input_quest_num(self, num='9999'):
        self.autoclicker.click(self.num_loc)
        sleep(0.1)
        self.autoclicker.type(num)
        sleep(0.1)
        self.autoclicker.click(self.yes_loc)
        sleep(0.1)

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

    def kill(self):
        self.combat.add_kills(1)

    def get_sample_probability(self, item_ids=None):
        probabilities = {}
        drops = self.drops.get_drops()
        if not item_ids or item_ids == []:
            item_ids = list(drops.keys())
        for item_id in item_ids:
            name = drops.get('name')
            count = drops.get(item_id).get('count')
            if name:
                probabilities[name] = count
            else:
                probabilities[item_id] = count
        return probabilities

    def print_drops(self):
        print('\nDrops:')
        for item_id, item_info in self.get_drops().items():
            print(f'{item_id} - {item_info}')

    def save_drops(self):
        self.drops.save()

    def add_to_db(self):
        self.drops.merge_db()


class AdvancedPlayer(Player):

    def __init__(self, resolution, quests, server, haste=0.5, cls='lr'):
        super().__init__(resolution, quests, haste=haste, cls=cls)
        self.sniffer = AqwPacketLogger(server=server)
        self.__fighting = CustomEvent(is_set=False)
        self.__pause_fight = CustomEvent(is_set=False)

    def add_drop(self, item_id, name, iQty=1, is_drop=False):
        if super().add_drop(item_id, name, iQty):
            if is_drop:
                self.acc_item()
            else:
                self.rej_item()
            turn_ins = self.quest.check_quest(self.drops)
            if any(x > 0 for x in list(turn_ins.values())):
                self.pause_fighting()
                self.toggle_log()
                for ti in list(turn_ins.values()):
                    if ti == 0:
                        continue
                    self.click_quest()
                    self.turn_in(ti)
                self.toggle_log()
                self.pause_fighting()

    def start_fighting(self):
        if self.__fighting.is_clear():
            self.__combat_loop()

    def stop_fighting(self):
        self.__pause_fight.clear()
        self.__fighting.clear()

    def __combat_loop(self):
        self.__fighting.set()
        self.__pause_fight.clear()
        while self.is_fighting():
            self.fight()
            self.__pause_fight.wait_for_clear()

    def pause_fighting(self):
        if self.__pause_fight.is_set():
            self.__pause_fight.clear()
        else:
            self.__pause_fight.set()

    def change_server(self, server):
        if self.sniffer.is_running():
            raise RuntimeError('Cannot switch servers while logging packets.')
        self.sniffer = AqwPacketLogger(server=server)

    def turn_in_quests(self, n):
        self.toggle_log()
        self.click_quest()
        self.turn_in(n)
        self.toggle_log()

    def is_fighting(self):
        return self.__fighting.is_set()


class AutoPlayer(AdvancedPlayer):

    def __init__(self, resolution, quests, server, haste=0.5, cls='lr'):
        super().__init__(resolution, quests, server, haste=haste, cls=cls)
        self.interpreter = Interpreter(self, self.sniffer)
        self.sniffer.set_concurrent_packet_summary_on(False)
        self.running = CustomEvent(False)
        self.__player_thread = None

    def start_sniff(self):
        self.sniffer.start()

    def start_interpreter(self):
        self.interpreter.start()

    def stop_sniff(self):
        self.sniffer.stop()

    def stop_interpreter(self):
        self.interpreter.stop()

    def run(self):
        self.running.set()
        self.start_sniff()
        self.start_interpreter()
        self.start_fighting()
        self.stop_sniff()
        self.stop_interpreter()
        self.stop_fighting()
        self.save_drops()
        self.add_to_db()
        self.running.clear()

    def start(self):
        self.__player_thread = Thread(target=self.run, daemon=True)
        self.__player_thread.name = 'player thread'
        self.__player_thread.start()

    def stop(self):
        self.running.clear()
        if self.interpreter.is_running():
            self.stop_interpreter()
        if self.sniffer.is_running():
            self.stop_sniff()
        if self.is_fighting():
            self.stop_fighting()

    def is_running(self):
        return self.running.is_set()

    def __print_sniffer_results(self):
        self.sniffer.print_jsons(exclude=['ct', 'uotls', 'mtls'])



