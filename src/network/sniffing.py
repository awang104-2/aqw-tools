from network.sending import send_dummy, get_host, get_random_port
from multiprocessing import Queue, Event, Process, set_start_method
from network.layers import Raw
from functools import partial
from scapy.all import sniff
from json import loads
import queue
import types
import time


try:
    set_start_method('spawn')
except RuntimeError:
    pass


SENTINEL = b'STOP'
DECODED_SENTINEL = 'STOP'


def drain(q, drain_q=None):
    if not drain_q:
        drain_q = queue.Queue()
    try:
        while True:
            json = q.get(block=False)
            drain_q.put(json)
    except queue.Empty:
        return drain_q


def gather_packets(bpf_filter, packets, stop_flag, drain_flag):
    prn = partial(log_packets, packets=packets)
    stop_filter = partial(_stop_filter, packets=packets, stop_flag=stop_flag)
    sniff(filter=bpf_filter, prn=prn, store=False, stop_filter=stop_filter)
    drain_flag.set()


def log_packets(packet, packets):
    if packet.haslayer(Raw):
        packets.put(packet)


def _stop_filter(packet, packets, stop_flag):
    boolean = stop_flag.is_set()
    if boolean:
        packets.put(packet)
    return stop_flag.is_set()


def gather_jsons(packets_queue, jsons_queue, packet_drain_flag, json_drain_flag):
    buffer = ''
    while not packet_drain_flag.is_set():
        jsons_list, buffer = parse_buffer(buffer)
        add_to_queue(jsons_list, jsons_queue)
        packet = packets_queue.get()
        buffer = update_buffer(buffer, packet)
    jsons_list, buffer = parse_buffer(buffer)
    add_to_queue(jsons_list, jsons_queue)
    json_drain_flag.set()


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
                    raise RuntimeError(f'Buffer: {buffer}\nIssue with parsing buffer at index {i}.')
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
        self.packets = Queue()
        self._packet_stop_flag = Event()
        self._packet_drain_flag = Event()
        self.packet_process = Process(
            name='Gather Packets',
            target=gather_packets,
            args=(self.bpf_filter, self.packets, self._packet_stop_flag, self._packet_drain_flag),
            daemon=self.daemon
        )

    def is_alive(self):
        return self.packet_process.is_alive()

    @property
    def bpf_filter(self):
        return f'({self._bpf_filter}) or (udp and dst host {self._ip_host} and dst port {self._port})'

    def start(self):
        self.packet_process.start()

    def stop(self):
        self._packet_stop_flag.set()
        send_dummy(local=False, payload=SENTINEL, port=self._port, verbose=False)
        self._packet_drain_flag.wait()
        self.packets = drain(self.packets)
        self._packet_drain_flag.clear()
        self.packet_process.join()

    def force_quit(self):
        if not self.is_alive():
            raise SnifferRunningError('Sniffer is not running.')
        self.packet_process.terminate()
        self.packet_process.join()

    def reset(self):
        self._packet_stop_flag.clear()
        self.packets = Queue()
        self.packet_process = Process(
            name='Gather Packets',
            target=gather_packets,
            args=(self.bpf_filter, self.packets, self._packet_stop_flag, self._packet_drain_flag),
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
        self.jsons = Queue()
        self._json_drain_flag = Event()
        self.json_process = Process(
            name='Gather JSONs',
            target=gather_jsons,
            args=(self.packets, self.jsons, self._packet_drain_flag, self._json_drain_flag),
            daemon=self.daemon
        )

    def start(self):
        self.packet_process.start()
        self.json_process.start()

    def stop(self, timeout=None):
        self._packet_stop_flag.set()
        send_dummy(local=False, payload=SENTINEL, port=self._port, verbose=False)
        self._json_drain_flag.wait()
        packets = self.packets
        self.packets = drain(self.packets)
        time.sleep(timeout)
        jsons = self.jsons
        self.jsons = drain(self.jsons)
        self.packet_process.join(timeout)
        self.json_process.join(timeout)
        try:
            while True:
                packet = packets.get(block=False)
                print('undrained packet:', packet.summary())
        except queue.Empty:
            pass
        try:
            while True:
                json = jsons.get(block=False)
                print('undrained json:', json)
                self.jsons.put(json)
        except queue.Empty:
            pass

    def force_quit(self):
        self.json_process.terminate()
        self.json_process.join()
        super().force_quit()

    def reset(self):
        super().reset()
        self.jsons = Queue()
        self.json_process = Process(
            name='Gather JSONs',
            target=gather_jsons,
            args=(self.packets, self.jsons, self._json_drain_flag),
            daemon=self.daemon
        )

    def get_json(self, block=True, timeout=None):
        try:
            return self.jsons.get(block=block, timeout=timeout)
        except queue.Empty:
            return None


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]


