from time import sleep
from bot.autoclicker import AutoClicker
from game.mechanics import Quests, Combat, Inventory
from threads.custom_threading import CustomEvent, LoopingThread
from network.sniffing import GameSniffer
from game.interpreter import Interpreter
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

    ITEM_ACCEPT_LOCATIONS = _clicking.get('ITEM ACCEPT')
    ITEM_REJECT_LOCATIONS = _clicking.get('ITEM REJECT')
    QUEST_LOG_LOCATIONS = _clicking.get('QUEST LOG')
    TURN_IN_LOCATIONS = _clicking.get('TURN IN')
    NUM_COMPLETE_LOCATIONS = _clicking.get('NUM COMPLETE')
    YES_LOCATIONS = _clicking.get('YES')

    def __init__(self, resolution, quests, server):
        self.acc_item_loc = Player.ITEM_ACCEPT_LOCATIONS.get(resolution)
        self.rej_item_loc = Player.ITEM_REJECT_LOCATIONS.get(resolution)
        self.quest_loc = Player.QUEST_LOG_LOCATIONS.get(resolution)
        self.turn_in_loc = Player.TURN_IN_LOCATIONS.get(resolution)
        self.num_loc = Player.NUM_COMPLETE_LOCATIONS.get(resolution)
        self.yes_loc = Player.YES_LOCATIONS.get(resolution)

        self.resolution = resolution
        self.server = server
        self.log_on = False
        self.delay_time = 0.1

        self.autoclicker = AutoClicker()
        self.hwnd = self.autoclicker.get_hwnd()
        self.sniffer = GameListener(server=self.server)
        self.sniffer.set_concurrent_packet_summary_on(False)
        self.interpreter = Interpreter(self, self.sniffer)
        self.__connected = CustomEvent(False)
        self.__autofight = LoopingThread(target=self.fight, daemon=True, loop=True)

    @property
    def autofight(self):
        return self.__autofight.running()

    @autofight.setter
    def autofight(self, fighting):
        if fighting and not self.__autofight.running():
            self.__autofight.start()
        elif not fighting and self.__autofight.running():
            self.__autofight.stop()
        else:
            raise RuntimeError('Cannot start or stop fighting if Player instance has already started or stopped fighting, respectively.')

    def toggle_autofight(self):
        current = self.autofight
        self.autofight = not self.autofight

    def delay(self):
        sleep(self.delay_time)

    def fight(self):
        move = self.combat.fight()
        if move:
            self.autoclicker.press(move)
            self.combat.sleep_gcd()
        else:
            self.delay()

    def click_quest(self):
        self.autoclicker.click(self.quest_loc)
        sleep(0.5)

    def turn_in(self, n):
        self.autoclicker.click(self.turn_in_loc)
        if n > 1:
            self.input_quest_num()
        sleep(0.75)

    def acc_item(self):
        self.autoclicker.click(self.acc_item_loc)
        sleep(0.25)

    def rej_item(self):
        self.autoclicker.click(self.rej_item_loc)
        sleep(0.25)

    def check_drop(self, accept):
        if accept:
            self.acc_item()
        else:
            self.rej_item()

    def add_item(self, item_id, name, iQty=1):
        self.add_drop(item_id, name, iQty)


    def add_drop(self, item_id, name, iQty=1):
        quest_reqs = self.quest.get_req_ids()
        is_required = self.drops.add(item_id, name, iQty, quest_reqs)
        self.check_drop(accept=is_required)

        return is_required

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

    def check_quests(self):
        turn_in_list = self.quest.check_quest(self.drops)
        return turn_in_list

    def turn_in_all(self, turn_in_list):
        self.autofight = False
        if any(x > 0 for x in list(turn_in_list.values())):
            for ti in list(turn_in_list.values()):
                if ti > 0:
                    self.turn_in_quests(ti)
        self.autofight = True

    def turn_in_quests(self, n):
        self.toggle_log()
        self.click_quest()
        self.turn_in(n)
        self.toggle_log()

    def connect(self):
        self.sniffer.start()
        self.interpreter.start()

    def disconnect(self):
        self.sniffer.stop()
        self.interpreter.stop()

    def __print_sniffer_results(self, include):
        self.sniffer.print_jsons(include=include)
