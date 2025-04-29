from network.sending import send_dummy_packet, get_host, get_random_port
from multiprocessing import Process, Queue, Event
from network.layers import Raw
from functools import partial
from scapy.all import sniff
from threading import Lock
from queue import Empty
import types


SENTINEL = b'STOP SNIFFING'


def stop_dummy(packet):
    if packet.haslayer(Raw):
        packet = packet[Raw].load
        if packet == SENTINEL:
            return True
        else:
            print('Recorded a JSON')
            return False
    else:
        return False

def stop_event(packet, event):
    return event.is_set()


class SnifferRunningError(RuntimeError):

    def __init__(self, msg):
        super().__init__(msg)


class Sniff(Process):

    def __init__(self, bpf_filter, stop_filter, layers, queue, *, daemon=False):
        self.layers = layers
        self.packets = queue
        self.bpf_filter = bpf_filter
        self.packet_count = 0
        self.stop_event = None
        self.stop_filter = stop_filter
        if not self.stop_filter:
            self.stop_event = Event()
            self.stop_filter = partial(stop_event, event=self.stop_event)
        super().__init__(name='Sniff Process', daemon=daemon)

    def run(self):
        print('running')
        sniff(filter=self.bpf_filter, prn=lambda packet: self.log_packets(packet), store=0, stop_filter=self.stop_filter)
        print('ran')

    def log_packets(self, packet):
        if self.layers:
            if any(packet.haslayer(layer) for layer in self.layers):
                self.packet_count += 1
                self.packets.put(packet)
        else:
            self.packet_count += 1
            self.packets.put(packet)


class Sniffer:

    def __init__(self, bpf_filter, stop_filter, layers: list | tuple = (), *, daemon=False, log=None):
        match stop_filter:
            case 'dummy':
                stop_filter = stop_dummy
            case 'event':
                stop_filter = None
        self._ip_host = get_host()[1]
        self._port = get_random_port()
        bpf_filter = f'({bpf_filter}) or (udp and dst host {self._ip_host} and dst port {self._port})'
        self.packets = Queue()
        self._process = Sniff(bpf_filter, stop_filter, layers, self.packets, daemon=daemon)
        self._lock = Lock()

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
            self._process.start()

    def stop(self, timeout=None):
        if self.running:
            with self._lock:
                if self._process.stop_event:
                    self._process.stop_event.set()
                else:
                    send_dummy_packet(local=False, payload=SENTINEL, port=self._port, verbose=False)
                    print('Sent Dummy')
                print('Joining')
                self._process.join(timeout)
                print('Joined.')

    def force_quit(self):
        with self._lock:
            try:
                self._process.terminate()
                self._process.join()
            except Exception as e:
                raise e

    def reset(self):
        if not self.running:
            with self._lock:
                layers =  self._process.layers
                bpf_filter, stop_filter = self._process.bpf_filter, self._process.stop_filter
                daemon = self._process.daemon
                self.packets = Queue()
                self._process = Sniff(bpf_filter, stop_filter, layers, self.packets, daemon=daemon)

    def get(self, timeout=None):
        try:
            return self.packets.get(timeout=timeout)
        except Empty:
            return None


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]