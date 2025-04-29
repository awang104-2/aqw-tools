from threading import Thread, Lock
from multiprocessing import Event, Process, Queue, active_children
from queue import Empty
from network import layers
from json import loads, decoder
from debug.logger import Logger


def print_all_processes():
    for child in active_children():
        print(f'Name: {child.name}, PID: {child.pid}')


MAX_STRING_SIZE = 999999
SENTINEL = b'STOP PROCESSING'


def decode(bytes_list, code='utf-8'):
    str_list = []
    for b in bytes_list:
        str_list.append(b.decode(encoding=code, errors='ignore'))
    return str_list


def get_raw(packet):
    if packet.haslayer(layers.Raw):
        return packet[layers.Raw].load
    else:
        return ''


def parse_bytes(bytes_obj):
    bytes_obj = bytes_obj.replace(b"\x00", b"")
    if bytes_obj == b'':
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

    def __init__(self, packets, jsons, *, daemon=False, log=None):
        self.buffer = ''
        self.buffer_changed = Event()
        self.packets = packets
        self.jsons = jsons
        self.flag = Event()
        self.return_value = Queue()
        self.log = log
        super().__init__(name='Process Packets Process', daemon=daemon)

    def update_buffer(self, buffer_lock, logger=None):
        if logger:
            logger.info('Started update buffer thread.')
        buffer_change = 0
        while self.flag.is_set():
            packet = self.packets.get()
            if packet == SENTINEL:
                self.flag.clear()
                self.buffer_changed.set()
                if logger:
                    logger.info('Stopped update buffer thread.')
                continue
            buffer_change += 1
            if logger:
                logger.info(f'Buffer Change #{buffer_change}')
            raw = get_raw(packet)
            blist = parse_bytes(raw)
            slist = decode(blist)
            if slist:
                for i, s in enumerate(slist):
                    with buffer_lock:
                        self.buffer += s
                    if logger and slist:
                        logger.info(f'Added to buffer {i + 1} time(s).')
                self.buffer_changed.set()

    def parse_buffer(self, buffer_lock, logger=None):
        if logger:
            logger.info('Started parse buffer thread.')
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
                                        json = loads(result)
                                        self.jsons.put(json)
                                    except decoder.JSONDecodeError:
                                        if logger:
                                            logger.error(f'Broken JSON: {result}')
                                elif depth < 0:
                                    end = i + 1
                                    break
                self.buffer = self.buffer[max(start, end):]
                self.buffer_changed.clear()
        if logger:
            logger.info('Stopped parse buffer thread.')

    def run(self):
        self.flag.set()
        buffer_lock = Lock()
        update_logger = Logger(self.log, 'buffer updater')
        update_logger.clear()
        parse_logger = Logger(self.log, 'buffer parser')
        parse_logger.clear()
        update_thread = Thread(target=self.update_buffer, name='Update Thread', args=[buffer_lock, update_logger])
        parse_thread = Thread(target=self.parse_buffer, name='Parse Thread', args=[buffer_lock, parse_logger])
        update_thread.start()
        parse_thread.run()
        update_thread.join()


class Processor:

    def __init__(self, sniffer, *, daemon=False, log=None):
        self.jsons = Queue()
        self.packets = sniffer.packets
        self._process = ProcessPackets(sniffer.packets, self.jsons, daemon=daemon, log=log)
        self._lock = Lock()
        self.logger = Logger(log, 'processor')

    @property
    def daemon(self):
        with self._lock:
            return self._process.daemon

    @daemon.setter
    def daemon(self, daemon):
        with self._lock:
            self._process.daemon = daemon

    @property
    def running(self):
        with self._lock:
            return self._process.is_alive()

    def start(self):
        with self._lock:
            self._process.start()

    def stop(self, timeout=None):
        if self.running:
            with self._lock:
                self.logger.info('Stopping Processor.')
                self._process.packets.put(SENTINEL)
                self._process.join(timeout)
                self.logger.info('Processor stopped.')

    def force_quit(self):
        with self._lock:
            try:
                self._process.terminate()
                self._process.join()
            except RuntimeError:
                self.logger.error('Processor forced shutdown failed.')

    def reset(self):
        self.logger.info('Resetting Processor.')
        if not self.running:
            with self._lock:
                self.jsons = Queue()
                packets, daemon, log = self._process.packets, self._process.daemon, self._process.log
                self._process = ProcessPackets(packets, self.jsons, daemon=daemon, log=log)
                self.logger.info('Processor reset.')
        else:
            self.logger.error('Processor reset failed: Processor was still running.')

    def get(self, timeout=None):
        try:
            return self.jsons.get(timeout=timeout)
        except Empty:
            return None


__all__ = [name for name in globals() if not name.startswith('-')]
