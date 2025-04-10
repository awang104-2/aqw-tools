from threading import Thread, Event, Lock
from queue import Queue, Empty
from network import layers
from json import loads, decoder


MAX_BUFFER_SIZE = 16384


def decode(bytes_list, code='utf-8'):
    str_list = []
    for b in bytes_list:
        str_list.append(b.decode(code))
    return str_list


def get_raw(packet):
    if packet.haslayer(layers.Raw):
        return packet[layers.Raw].load
    else:
        return ''


def parse_bytes(bytes_obj, limit=200):
    if bytes_obj == '':
        return []
    if len(bytes_obj) < limit:
        return [bytes_obj]
    else:
        first_half = [bytes_obj[:limit]]
        second_half = bytes_obj[limit:]
        return first_half + parse_bytes(second_half)


class Processor:

    EmptyError = Empty

    def __init__(self, sniffer, timeout=0.05):
        # Protected attributes for internal functionality
        self._buffer_lock = Lock()
        self._flag = Event()
        self._flag.set()
        self._buffer_changed = Event()
        self._clean_buffer = Event()
        self._clean_buffer.set()

        # Protected attributes for threading
        self._update_buffer_thread = Thread(target=self._update_buffer_loop, name='processor thread internal-1', daemon=True)
        self._parse_buffer_thread = Thread(target=self._parse_buffer_loop, name='processor thread internal-2', daemon=True)
        self._interpret_json_thread = Thread(target=self._interpret_json_loop, name='processor thread internal-3', daemon=True)

        # Public and protected attributes for bookkeeping
        self._buffer = ''
        self.missed_packets = 0

        # Public attributes
        self.sniffer = sniffer
        self.jsons = Queue()
        self.print = Event()
        self.timeout = timeout

    @property
    def running(self):
        return self._parse_buffer_thread.is_alive()

    @property
    def ready(self):
        return not self._parse_buffer_thread.is_alive()

    def start(self):
        self._flag.set()
        self._update_buffer_thread.start()
        self._parse_buffer_thread.start()
        self._interpret_json_thread.start()

    def stop(self):
        self._flag.clear()

    def reset(self):
        self._update_buffer_thread = Thread(target=self._update_buffer_loop, name='processor thread internal-1', daemon=True)
        self._parse_buffer_thread = Thread(target=self._parse_buffer_loop, name='processor thread internal-2', daemon=True)
        self._interpret_json_thread = Thread(target=self._interpret_json_loop, name='processor thread internal-3', daemon=True)
        self.missed_packets = 0
        self._buffer = ''

    def update_buffer(self):
        packet = self.sniffer.get(timeout=self.timeout)
        if packet:
            raw = get_raw(packet)
            blist = parse_bytes(raw)
            slist = decode(blist)
            with self._buffer_lock:
                for s in slist:
                    self._buffer += s
                    self._buffer_changed.set()

    def parse_buffer(self):
        self._buffer_changed.wait(self.timeout)
        start, end, depth, quoted, escaped = (-1, -1, 0, False, False)
        with self._buffer_lock:
            for i, char in enumerate(self._buffer):
                if char == '{':
                    if depth == 0:
                        start = i
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        end = i
                        try:
                            result = self._buffer[start:end + 1]
                            self.jsons.put(loads(result))
                        except decoder.JSONDecodeError:
                            print(f'Decode Error - {result}')
                            self.missed_packets += 1
            if self._clean_buffer.is_set():
                self._buffer = self._buffer[end + 1:]
        self._buffer_changed.clear()

    def interpret(self, *args, **kwargs):
        try:
            if self.print.is_set():
                self.get_and_print_packet()
        except Processor.EmptyError:
            return

    def _update_buffer_loop(self):
        while self.sniffer.running and self._flag.is_set():
            self.update_buffer()

    def _parse_buffer_loop(self):
        while self.sniffer.running and self._flag.is_set():
            self.parse_buffer()

    def _interpret_json_loop(self):
        while self.sniffer.running and self._flag.is_set():
            self.interpret()

    def get_packet(self):
        return self.jsons.get(timeout=self.timeout)

    def get_and_print_packet(self):
        packet = self.get_packet()
        if packet:
            print(packet)

    def join(self, timeout=None):
        self._update_buffer_thread.join(timeout)
        self._parse_buffer_thread.join(timeout)
        self._interpret_json_thread.join(timeout)


__all__ = [name for name in globals() if not name.startswith('-')]



