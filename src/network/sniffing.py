import multiprocessing
import threading
from network.sending import send_dummy, get_host, get_random_port
from multiprocessing import Process, Event, Queue
from network.layers import Raw
from scapy.all import sniff
from json import loads, decoder
import queue
import types


SENTINEL = b'STOP PROCESS'


def drain(q, drain_q=None):
    if not drain_q:
        drain_q = queue.Queue()
    try:
        while True:
            json = q.get_nowait()
            drain_q.put(json)
    except queue.Empty:
        return drain_q


def process(packets, jsons_queue, stop_flag):
    buffer = ''
    while True:
        packet = packets.get()
        if packet == SENTINEL:
            break
        buffer = update_buffer(buffer, packet)
        jsons_list, buffer = parse_buffer(buffer)
        for json in jsons_list:
            jsons_queue.put(json)
    stop_flag.set()


def update_buffer(buffer, packet):
    raw = get_raw(packet)
    if raw:
        raw = erase_padding(raw)
        buffer += raw.decode('UTF-8', 'strict')
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
                    print('buffer', buffer[i:])
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
                    print(buffer)
                    raise RuntimeError(f'Issue with parsing buffer at index {i}.')
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

    def __init__(self, bpf_filter, layers: list | tuple = (), *, daemon=False):
        self._ip_host = get_host()[1]
        self._port = get_random_port()
        self._bpf_filter = bpf_filter
        self.daemon = daemon
        self.layers = layers
        self.packets = Queue()
        self._stop_flag = Event()
        self.packet_process = Process(name='Packet Gathering Process', target=self.sniff, daemon=self.daemon)

    def is_alive(self):
        return self.packet_process.is_alive()

    @property
    def bpf_filter(self):
        return f'({self._bpf_filter}) or (udp and dst host {self._ip_host} and dst port {self._port})'

    def stop_filter(self, packet):
        return self._stop_flag.is_set()

    def sniff(self):
        sniff(filter=self.bpf_filter, prn=self.log_packets, store=False, stop_filter=self.stop_filter)
        packets = drain(self.packets)
        print(self.packets.empty())
        self.packets = packets
        print(multiprocessing.active_children(), threading.enumerate())

    def start(self):
        self.packet_process.start()

    def log_packets(self, packet):
        if self.layers:
            if any(packet.haslayer(layer) for layer in self.layers):
                self.packets.put(packet)
        else:
            self.packets.put(packet)

    def stop(self):
        if not self.packet_process.is_alive():
            raise SnifferRunningError('packet_process is not running.')
        self._stop_flag.set()
        print('stop flag set')
        send_dummy(local=False, payload=SENTINEL, port=self._port, verbose=False)
        print('dummy sent')
        self.packet_process.join()
        print('joined')

    def force_quit(self):
        if not self.is_alive():
            raise SnifferRunningError('Sniffer is not running.')
        self.packet_process.terminate()
        self.packet_process.join()

    def reset(self):
        self._stop_flag.clear()
        self.packets = Queue()
        self.packet_process = Process(name='Sniff Process', target=self.sniff, daemon=self.daemon)

    def get_packet(self, *, timeout=None, no_wait):
        if no_wait:
            try:
                return self.packets.get_nowait()
            except queue.Empty:
                return None
        else:
            return self.packets.get(timeout)


class JsonSniffer(Sniffer):

    def __init__(self, bpf_filter, *, daemon=False):
        super().__init__(bpf_filter=bpf_filter, layers=[Raw], daemon=daemon)
        self.jsons = Queue()
        self.__stop_flag = Event()
        self.json_process = Process(name='Json Extraction Process', target=process, args=(self.packets, self.jsons, self.__stop_flag), daemon=self.daemon)

    def log_packets(self, packet):
        if packet.haslayer(self.layers[0]):
            self.packets.put(packet)

    def start(self):
        self.packet_process.start()
        self.json_process.start()

    def stop(self, timeout=None):
        if not self.json_process.is_alive():
            raise SnifferRunningError('json_process is not running.')
        self.packets.put(SENTINEL)
        print('sentinel')
        self.__stop_flag.wait()
        print('waiting')
        self.jsons = drain(self.jsons)
        print('drained')
        self.json_process.join(timeout)
        print('joined')
        super().stop()

    def force_quit(self):
        self.json_process.terminate()
        self.json_process.join()
        super().force_quit()

    def reset(self):
        super().reset()
        self.jsons = Queue()
        self.json_process = Process(target=process, args=(self.packets, self.jsons), daemon=self.daemon)

    def get_json(self, *, timeout=None, no_wait):
        if no_wait:
            try:
                return self.jsons.get_nowait()
            except queue.Empty:
                return None
        else:
            return self.jsons.get(timeout)


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]


