from network.processing import Processor
from threading import Thread, Lock
from game.aqw_backend import *
from decorators import *


class JsonDict:

    def __init__(self, dictionary=None):
        self._lock = Lock()
        if dictionary:
            self._jsons = dictionary
        else:
            self._jsons = dict.fromkeys(list(AQW_PACKETS.keys()), [])

    @with_lock
    def __str__(self):
        return str(self._jsons)

    @with_lock
    def __getitem__(self, item):
        return self._jsons.get(item)

    @with_lock
    def __setitem__(self, key, value):
        self._jsons[key] = value

    @with_lock
    def get(self, key):
        return self._jsons.get(key)

    @with_lock
    def add(self, key, json):
        self._jsons[key].append(json)

    @with_lock
    def adds(self, key, jsons):
        self._jsons[key] += jsons

    @with_lock
    def update(self, jsons_dictionary):
        for key, json_list in jsons_dictionary.items():
            self.adds(key, json_list)

    @with_lock
    def to_dict(self):
        return self._jsons

    @with_lock
    def clear(self):
        self._jsons = dict.fromkeys(list(AQW_PACKETS.keys()), [])

    @with_lock
    def pop(self, key):
        return self._jsons.pop(key)

    @with_lock
    def pop_all(self):
        jsons = self._jsons
        self._jsons = dict.fromkeys(list(AQW_PACKETS.keys()), [])
        return jsons


class Interpreter(Processor):

    def __init__(self, character, sniffer, delay=None):
        super().__init__(sniffer)
        self.sniffer = sniffer
        self.character = character
        self._interpret_thread = Thread(target=self._interpret, name='interpreter thread', daemon=False, loopable=True)
        self.delay = delay
        self._sorted_jsons = None
        self._custom_functions = {}

    def parse_buffer(self):
        start, end, start_bracket_count, end_bracket_count = (0, 0, 0, 0)
        for i, char in enumerate(self._buffer):
            if char == '{':
                if start_bracket_count == 0:
                    start = i
                start_bracket_count += 1
            elif char == '}':
                end_bracket_count += 1
                if start_bracket_count == end_bracket_count != 0:
                    end = i
                    result, self._buffer = self._buffer[start:end + 1], self._buffer[end + 1:]
                    return loads(result)['b']['o']

        raise ValueError(f'Incomplete or incompatible string for JSON object parsing: {self._buffer}.')

    @check_running
    def set_delay(self, delay):
        self.delay = delay

    @check_running
    def clear_delay(self):
        self.delay = None

    def _add_item(self, added_item_jsons):
        for item in added_item_jsons:
            item_id = list(item.get('items').keys())[0]
            name = item.get('items').get(item_id).get('sName')
            iQty = item.get('items').get(item_id).get('iQty')
            self.character.add_item(item_id=item_id, name=name, iQty=iQty)
            iQtyNow = item.get('items').get(item_id).get('iQtyNow', None)
            if iQtyNow:
                self.character.set_inventory(item_id, iQtyNow)

    def _add_drops(self, drop_jsons):
        for drop in drop_jsons:
            item_id = list(drop.get('items').keys())[0]
            name = drop.get('items').get(item_id).get('sName')
            iQty = drop.get('items').get(item_id).get('iQty')
            self.character.add_drop(item_id=item_id, name=name, iQty=iQty)

    def _add_kills(self, kill_jsons):
        for kill in kill_jsons:
            kill.get('id')
            self.character.kill()

    def _adjust_haste(self, stat_update_jsons):
        for stat_update in stat_update_jsons:
            haste = stat_update.get('sta').get('$tha')
            if haste:
                self.character.haste = haste

    def _record_combat_data(self, combat_jsons):
        for combat_json in combat_jsons:
            pass

    def _malgor_message(self, combat_jsons):
        for json in combat_jsons:
            anims = json.get('anims')
            if anims:
                msg = anims[0].get('msg')
                match msg:
                    case self.MALGOR_TRUTH:
                        pass
                    case self.MALGOR_LISTEN:
                        pass
                    case self.MALGOR_RED:
                        pass

    @check_not_running
    def add_custom_function(self, *, key, function):
        self._custom_functions[function] = key

    def _run_custom_functions(self, sorted_jsons):
        for function, key in self._custom_functions.items():
            jsons = sorted_jsons.get(key, [])
            function(jsons)

    def interpret(self, sorted_jsons):
        self._add_item(sorted_jsons.get('addItems', []))
        self._add_drops(sorted_jsons.get('dropItem',[]))
        self._add_kills(sorted_jsons.get('addGoldExpM',[]))
        self._adjust_haste(sorted_jsons.get('stu', []))
        self._record_combat_data('ct', [])
        self._run_custom_functions(sorted_jsons)

    def _interpret(self):
        if self.sniffer.running() and self.running():
            self.sniffer.wait_for_packet(timeout=1)
            self.interpret(self.sniffer.get_sorted())

    def running(self):
        return self._interpret_thread.running()

    @check_running
    def run(self):
        self._interpret_thread.run()

    @check_running
    def start(self):
        self._interpret_thread.start()

    def stop(self):
        self._interpret_thread.stop()

    def get(self, key):
        return self._jsons.get(key)

    def get_all(self):
        return self._jsons

    def pop(self, key):
        return self._jsons.pop(key)

    def pop_all(self):
        return self._jsons.pop_all()