from threading import Thread, Event, Lock
from network import layers
from json import loads
count = 0


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

    def __init__(self, sniffer):
        self._buffer_lock = Lock()
        self._sniffer = sniffer
        self._buffer = ''
        self._update_buffer_thread = Thread(target=self._update_buffer, name='processor thread internal-1', daemon=True)
        self._parse_buffer_thread = Thread(target=self._parse_buffer, name='processor thread internal-2', daemon=True)
        self._flag = Event()
        self._flag.set()
        self._buffer_changed = Event()

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

    def stop(self):
        self._flag.clear()

    def reset(self):
        self._update_buffer_thread = Thread(target=self._update_buffer, daemon=True)
        self._parse_buffer_thread = Thread(target=self._parse_buffer, daemon=True)
        self._buffer = ''

    def get_packet(self, timeout):
        return self._sniffer.get(timeout)

    def update_buffer(self, packet):
        if packet:
            raw = get_raw(packet)
            blist = parse_bytes(raw)
            slist = decode(blist)
            with self._buffer_lock:
                for s in slist:
                    self._buffer_changed.set()
                    self._buffer += s

    def _update_buffer(self):
        while self._sniffer.running and self._flag.is_set():
            packet = self.get_packet(0.05)
            self.update_buffer(packet)

    def parse_buffer(self):
        global count
        count += 1
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
                    if 'listen' in self._buffer:
                        print(f'BUFFER {count}', self._buffer)
                    result, self._buffer = self._buffer[start:end + 1], self._buffer[end + 1:]
                    if 'listen' in result:
                        print(f'RESULT {count}', result)
                    return loads(result)
        count -= 1
        raise ValueError(f'Incomplete or incompatible string for JSON object parsing: {self._buffer}.')

    def parse_buffer_loop(self):
        jsons = []
        with self._buffer_lock:
            while True:
                try:
                    json = self.parse_buffer()
                    jsons.append(json)
                except ValueError:
                    return jsons

    def process(self, timeout):
        self._buffer_changed.wait(timeout)
        jsons = self.parse_buffer_loop()
        for json in jsons:
            print(json['b']['o'])
        self._buffer_changed.clear()

    def _parse_buffer(self):
        while self._sniffer.running and self._flag.is_set():
            self.process(0.05)


__all__ = [name for name in globals() if not name.startswith('-')]



