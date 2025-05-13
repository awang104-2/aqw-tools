from network.sending import send_dummy, get_host, get_random_port
from network.layers import Raw
from functools import partial
from scapy.all import sniff
from json import loads
import threading
import multiprocessing
import queue
import types
import time


try:
    multiprocessing.set_start_method('spawn')
except RuntimeError:
    pass


SENTINEL = b'STOP'
DECODED_SENTINEL = 'STOP'


def check_threads(t):
    time.sleep(t)
    for thread in threading.enumerate():
        print(f'{thread} | {thread.name} | {thread.is_alive()} | {thread.daemon}')


def gather_packets(bpf_filter, packets_queue, stop_flag):
    prn = partial(log_packets, packets=packets_queue)
    stop_filter = partial(_stop_filter, stop_flag=stop_flag)
    sniff(filter=bpf_filter, prn=prn, store=False, stop_filter=stop_filter)


def log_packets(packet, packets):
    if packet.haslayer(Raw):
        packets.put(packet)


def _stop_filter(packet, stop_flag):
    return stop_flag.is_set()


def gather_jsons(packets_queue, jsons_queue, stop_flag):
    buffer = ''
    while True:
        try:
            packet = packets_queue.get(timeout=0.1)
            buffer = update_buffer(buffer, packet)
            jsons_list, buffer = parse_buffer(buffer)
            add_to_queue(jsons_list, jsons_queue)
        except queue.Empty:
            if stop_flag.is_set():
                break


def add_to_queue(jsons_list, json_queue):
    for json in jsons_list:
        json_queue.put(json)


def update_buffer(buffer, packet):
    raw = get_raw(packet)
    if raw:
        raw = erase_padding(raw)
        try:
            buffer += raw.decode('UTF-8', 'strict')
        except Exception as e:
            print(f'Error: {e}')
            raise e
    return buffer


def parse_buffer(buffer):
    jsons = []
    start, end, depth, quoted, escaped, in_string = (0, 0, 0, False, False, False)
    for i, char in enumerate(buffer):
        match char:
            case '"':
                in_string = not in_string
            case '{' if not in_string:
                if depth == 0:
                    start = i
                depth += 1
            case '}' if not in_string:
                depth -= 1
                if depth == 0:
                    end = i + 1
                    result = buffer[start:end]
                    json = loads(result)
                    jsons.append(json)
                elif depth < 0:
                    raise RuntimeError(f'Buffer: {buffer}\nIssue with parsing buffer at index {i}, substring "{buffer[max(i - 5, 0):min(i + 5, len(buffer) - 1)]}".')
    return jsons, buffer[max(start, end):]


def get_raw(packet):
    if packet.haslayer(Raw):
        return packet[Raw].load
    else:
        return None


def erase_padding(bytes_object):
    return bytes_object.replace(b'\x00', b'')


class ProcessorRunningError(RuntimeError):

    def __init__(self, msg):
        super().__init__(msg)


class SnifferRunningError(RuntimeError):

    def __init__(self, msg):
        super().__init__(msg)


class Sniffer:

    def __init__(self, bpf_filter, *, daemon=False):
        self._ip_host = get_host()[1]
        self._port = get_random_port()
        self._bpf_filter = bpf_filter
        self.daemon = daemon
        self.packets = multiprocessing.Queue()
        self._stop_flag = multiprocessing.Event()
        self._packet_process = multiprocessing.Process(
            name='Gather Packets',
            target=gather_packets,
            args=(self.bpf_filter, self.packets, self._stop_flag),
            daemon=self.daemon
        )

    def is_alive(self):
        return self._packet_process.is_alive()

    @property
    def bpf_filter(self):
        return f'({self._bpf_filter}) or (udp and dst host {self._ip_host} and dst port {self._port})'

    def start(self):
        self._packet_process.start()

    def stop(self):
        self._stop_flag.set()
        send_dummy(local=False, payload=SENTINEL, port=self._port, verbose=False)
        self._packet_process.join()

    def force_quit(self):
        self._packet_process.terminate()
        self._packet_process.join()

    def reset(self):
        self._stop_flag.clear()
        self.packets = multiprocessing.Queue()
        self._packet_process = multiprocessing.Process(
            name='Gather Packets',
            target=gather_packets,
            args=(self.bpf_filter, self.packets, self._stop_flag),
            daemon=self.daemon
        )

    def get_packet(self, block=True, timeout=None):
        try:
            return self.packets.get(block=block, timeout=timeout)
        except queue.Empty:
            return None


class JsonSniffer(Sniffer):

    def __init__(self, bpf_filter, *, daemon=False):
        super().__init__(bpf_filter=bpf_filter, daemon=daemon)
        self.jsons = queue.Queue()
        self._json_thread = threading.Thread(
            name='Gather JSONs',
            target=gather_jsons,
            args=(self.packets, self.jsons, self._stop_flag),
            daemon=self.daemon
        )

    def start(self):
        self._packet_process.start()
        self._json_thread.start()

    def stop(self, timeout=None):
        self._stop_flag.set()
        send_dummy(local=False, payload=SENTINEL, port=self._port, verbose=False)
        self._packet_process.join(timeout)
        self._json_thread.join(timeout)

    def force_quit(self):
        super().force_quit()
        self._stop_flag.set()
        self._json_thread.join()

    def reset(self):
        super().reset()
        self.jsons = multiprocessing.Queue()
        self._json_thread = multiprocessing.Process(
            name='Gather JSONs',
            target=gather_jsons,
            args=(self.packets, self.jsons, self._stop_flag),
            daemon=self.daemon
        )

    def get_json(self, block=True, timeout=None):
        try:
            return self.jsons.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def is_alive(self):
        return self._packet_process.is_alive() or self._json_thread.is_alive()


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]


