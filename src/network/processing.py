from threading import Thread, Lock
from multiprocessing import Event, Process, Queue
from queue import Empty
from network import layers
from json import loads, decoder


MAX_STRING_SIZE = 5000
SENTINEL = 'STOP COMMAND PROCESSING'


def decode(bytes_list, code='utf-8'):
    str_list = []
    for b in bytes_list:
        str_list.append(b.decode(code, errors='ignore'))
    return str_list


def get_raw(packet):
    if packet.haslayer(layers.Raw):
        return packet[layers.Raw].load
    else:
        return ''


def parse_bytes(bytes_obj):
    bytes_obj = bytes_obj.replace(b"\x00", b"")
    if bytes_obj == '':
        return []
    if len(bytes_obj) < MAX_STRING_SIZE:
        return [bytes_obj]
    else:
        first_half = [bytes_obj[:MAX_STRING_SIZE]]
        second_half = bytes_obj[MAX_STRING_SIZE:]
        return first_half + parse_bytes(second_half)


class ProcessorRunningError(RuntimeError):

    def __init__(self, msg):
        super().__init__(msg)


class ProcessPackets(Process):

    def __init__(self, packets, jsons, flag, *, daemon=False):
        self.buffer = ''
        self.buffer_changed = Event()
        self.packets = packets
        self.jsons = jsons
        self.flag = flag
        self.return_value = Queue()
        super().__init__(name='Process Packets Process', daemon=daemon)

    def update_buffer(self, buffer_lock):
        while self.flag.is_set():
            packet = self.packets.get()
            if packet == SENTINEL:
                self.buffer_changed.set()
                continue
            if packet:
                raw = get_raw(packet)
                blist = parse_bytes(raw)
                slist = decode(blist)
                with buffer_lock:
                    for s in slist:
                        self.buffer += s
                        self.buffer_changed.set()

    def parse_buffer(self, buffer_lock):
        while self.flag.is_set():
            self.buffer_changed.wait()
            start, end, depth, quoted, escaped, in_string = (0, 0, 0, False, False, False)
            with buffer_lock:
                for i, char in enumerate(self.buffer):
                    if escaped:
                        escaped = False
                    else:
                        match char:
                            case '"':
                                in_string = not in_string
                            case '\\':
                                escaped = True
                            case '{' if not in_string:
                                if depth == 0:
                                    start = i
                                depth += 1
                            case '}' if not in_string:
                                depth -= 1
                                if depth == 0:
                                    end = i + 1
                                    try:
                                        result = self.buffer[start:end]
                                        self.jsons.put(loads(result))
                                    except decoder.JSONDecodeError:
                                        pass
                self.buffer = self.buffer[max(start, end):]
                self.buffer_changed.clear()

    def run(self):
        buffer_lock = Lock()
        update_thread = Thread(target=self.update_buffer, name='Update Thread', args=[buffer_lock])
        parse_thread = Thread(target=self.parse_buffer, name='Parse Thread', args=[buffer_lock])
        update_thread.start()
        parse_thread.start()
        update_thread.join()
        parse_thread.join()


class Processor:

    def __init__(self, sniffer, *, daemon=False):
        self.jsons = Queue()
        self._flag = Event()
        self._process = ProcessPackets(sniffer.packets, self.jsons, self._flag, daemon=daemon)

    @property
    def daemon(self):
        return self._process.daemon

    @daemon.setter
    def daemon(self, daemon):
        self._process.daemon = daemon

    @property
    def running(self):
        return self._process.is_alive()

    def start(self):
        self._flag.set()
        self._process.start()

    def stop(self, force=True):
        self._flag.clear()
        self._process.packets.put(SENTINEL)
        self._process.join(0.5)
        if self._process.is_alive():
            if force:
                self._process.terminate()
                self._process.join()
            else:
                raise RuntimeError('Processor shutdown failed.')

    def reset(self):
        if self._process.is_alive():
            raise ProcessorRunningError('Cannot reset while Sniffer is running.')
        self.jsons = Queue()
        self._flag.clear()
        packets, daemon = self._process.packets, self._process.daemon
        self._process = ProcessPackets(packets, self.jsons, self._flag, daemon=daemon)

    def join(self, timeout=None):
        self._process.join(timeout)

    def get(self, timeout=None):
        try:
            return self.jsons.get(timeout=timeout)
        except Empty:
            return None


__all__ = [name for name in globals() if not name.startswith('-')]


