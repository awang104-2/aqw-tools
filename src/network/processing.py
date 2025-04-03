from threading import Thread, Event, Lock
from network import layers
from json import loads


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

    def __init__(self, sniffer):
        self._buffer_lock = Lock()
        self._sniffer = sniffer
        self._buffer = ''
        self._update_buffer_thread = Thread(target=self._update_buffer_loop, name='processor thread internal-1', daemon=True)
        self._parse_buffer_thread = Thread(target=self._parse_buffer_loop, name='processor thread internal-2', daemon=True)
        self._flag = Event()
        self._flag.set()
        self._buffer_changed = Event()
        self._string_size_list = 0

    @property
    def running(self):
        return self._parse_buffer_thread.is_alive()

    @property
    def ready(self):
        return not self._parse_buffer_thread.is_alive()

    @property
    def buffer_size(self):
        with self._buffer_lock:
            return {'buffer': len(self._buffer), 'packets': self._string_size_list}

    def start(self):
        self._flag.set()
        self._update_buffer_thread.start()
        self._parse_buffer_thread.start()

    def stop(self):
        self._flag.clear()

    def reset(self):
        self._update_buffer_thread = Thread(target=self._update_buffer_loop, name='processor thread internal-1', daemon=True)
        self._parse_buffer_thread = Thread(target=self._parse_buffer_loop, name='processor thread internal-2', daemon=True)
        self._buffer = ''

    def get_packet(self, timeout):
        return self._sniffer.get(timeout)

    def _update_buffer(self, packet):
        if packet:
            raw = get_raw(packet)
            blist = parse_bytes(raw)
            slist = decode(blist)
            with self._buffer_lock:
                for s in slist:
                    self._string_size_list += len(s)
                    self._buffer += s
                    self._buffer_changed.set()

    def update_buffer(self, packet):
        self._update_buffer(packet)

    def _update_buffer_loop(self):
        while self._sniffer.running and self._flag.is_set():
            packet = self.get_packet(0.05)
            self._update_buffer(packet)

    def _parse_buffer_once(self):
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
                    return loads(result)
        raise ValueError(f'Incomplete or incompatible string for JSON object parsing: {self._buffer}.')

    def _parse_buffer(self):
        jsons = []
        with self._buffer_lock:
            while True:
                try:
                    json = self._parse_buffer_once()
                    jsons.append(json)
                except ValueError:
                    return jsons

    def parse_buffer(self, timeout=None):
        self._buffer_changed.wait(timeout)
        jsons = self._parse_buffer()
        self._buffer_changed.clear()
        return jsons

    def _parse_buffer_loop(self):
        while self._sniffer.running and self._flag.is_set():
            self.parse_buffer(0.05)


__all__ = [name for name in globals() if not name.startswith('-')]



