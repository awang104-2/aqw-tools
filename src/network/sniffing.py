from network.sending import send_dummy, get_host, get_random_port
from multiprocessing import Process, Event, Queue
from threading import Thread, RLock, Lock
from network.layers import Raw
from scapy.all import sniff
from json import loads
import queue
import types
import time


SENTINEL = b'STOP SNIFFING'


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


class Sniff(Process):

    def __init__(self, bpf_filter, layers, packet_queue, *, stop_flag=Event(), daemon=False):
        self.layers = layers
        self.packets = packet_queue
        self.bpf_filter = bpf_filter
        self.stop_flag = stop_flag
        super().__init__(name='Sniff Process', daemon=daemon)

    def stop_filter(self, packet):
        return self.stop_flag.is_set()

    def run(self):
        sniff(filter=self.bpf_filter, prn=self.log_packets, store=False, stop_filter=self.stop_filter)

    def log_packets(self, packet):
        if self.layers:
            if any(packet.haslayer(layer) for layer in self.layers):
                self.packets.put(packet)
        else:
            self.packets.put(packet)


class ProcessPackets(Process):

    def __init__(self, packets, jsons, *, daemon=False):
        self.buffer = ''
        self.buffer_changed = Event()
        self.packets = packets
        self.jsons = jsons
        self.return_value = Queue()
        self.stop_flag = Event()
        super().__init__(name='Process Packets Process', daemon=daemon)

    def update_buffer(self, buffer_lock):
        while True:
            packet = self.packets.get()
            if packet == SENTINEL:
                self.buffer_changed.set()
                self.stop_flag.set()
                break
            raw = get_raw(packet)
            if raw:
                with buffer_lock:
                    raw = erase_padding(raw)
                    self.buffer += raw.decode('UTF-8', 'ignore')
                    self.buffer_changed.set()

    def parse_buffer(self, buffer_lock):
        while not self.stop_flag.is_set():
            self.buffer_changed.wait()
            with buffer_lock:
                start, end, depth, quoted, escaped, in_string = (0, 0, 0, False, False, False)
                for i, char in enumerate(self.buffer):
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
                                result = self.buffer[start:end]
                                json = loads(result)
                                self.jsons.put(json)
                            elif depth < 0:
                                print(self.buffer)
                                raise RuntimeError(f'Issue with parsing buffer at index {i}.')
                self.buffer = self.buffer[max(start, end):]
                self.buffer_changed.clear()

    def run(self):
        buffer_lock = Lock()
        update_thread = Thread(target=self.update_buffer, name='Update Thread', args=[buffer_lock])
        parse_thread = Thread(target=self.parse_buffer, name='Parse Thread', args=[buffer_lock])
        update_thread.start()
        parse_thread.run()
        update_thread.join()


class Sniffer:

    def __init__(self, bpf_filter, layers: list | tuple = (), *, daemon=False):
        self._ip_host = get_host()[1]
        self._port = get_random_port()
        self.stop_flag = Event()
        self.packets = Queue()
        bpf_filter = f'({bpf_filter}) or (udp and dst host {self._ip_host} and dst port {self._port})'
        self._process = Sniff(bpf_filter, layers, self.packets, daemon=daemon, stop_flag=self.stop_flag)
        self._lock = RLock()

    @property
    def filter(self):
        with self._lock:
            return self._process.bpf_filter

    @property
    def layers(self):
        with self._lock:
            return self._process.layers

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
            if self.running:
                raise SnifferRunningError('Stop Sniffer first.')
            self._process.start()

    def stop(self, timeout=None):
        with self._lock:
            if not self.running:
                raise SnifferRunningError('Sniffer is not running.')
            self.stop_flag.set()
            send_dummy(local=False, payload=SENTINEL, port=self._port, verbose=False)
            time.sleep(0.1)
            drained_queue = queue.Queue()
            while not self.packets.empty():
                packet = self.get()
                drained_queue.put(packet)
            self.packets = drained_queue
            self._process.join(timeout)

    def force_quit(self):
        with self._lock:
            if not self.running:
                raise SnifferRunningError('Sniffer is not running.')
            self._process.terminate()
            self._process.join()

    def reset(self):
        with self._lock:
            if self.running:
                raise SnifferRunningError('Stop Sniffer first.')
            bpf_filter, layers, daemon = self._process.bpf_filter, self._process.layers, self._process.daemon
            self.packets = Queue()
            self.stop_flag = Event()
            self._process = Sniff(bpf_filter, layers, self.packets, daemon=daemon, stop_flag=self.stop_flag)

    def get(self, timeout=None):
        try:
            return self.packets.get(timeout=timeout)
        except queue.Empty:
            return None

    def empty(self):
        return self.packets.empty()


class JsonSniffer(Sniffer):

    def __init__(self, bpf_filter, layers: list | tuple = (), *, daemon=False):
        super().__init__(bpf_filter, layers, daemon=daemon)
        self.jsons = Queue()
        self._process = ProcessPackets(self.packets, self.jsons, daemon=daemon)

    @property
    def running(self):
        with self._lock:
            return super().running and self._process.is_alive()

    def start(self):
        with self._lock:
            super().start()
            self._process.start()

    def stop(self, timeout=None):
        with self._lock:
            self._process.packets.put(SENTINEL)
            self._process.join(timeout)
            super().stop()

    def force_quit(self):
        with self._lock:
            self._process.terminate()
            self._process.join()
            super().force_quit()

    def reset(self):
        with self._lock:
            super().reset()
            self.jsons = Queue()
            packets, daemon = self._process.packets, self._process.daemon
            self._process = ProcessPackets(packets, self.jsons, daemon=daemon)

    def get(self, timeout=None):
        try:
            return self.jsons.get(timeout=timeout)
        except queue.Empty:
            return None


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]


