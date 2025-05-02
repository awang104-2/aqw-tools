from network.sending import send_dummy_packet, get_host, get_random_port
from multiprocessing import Process, Queue, Event
from scapy.all import sniff
from threading import Lock
from queue import Empty
import types


SENTINEL = b'STOP SNIFFING'


class SnifferRunningError(RuntimeError):

    def __init__(self, msg):
        super().__init__(msg)


class Sniff(Process):

    def __init__(self, bpf_filter, layers, queue, *, daemon=False):
        self.layers = layers
        self.packets = queue
        self.bpf_filter = bpf_filter
        self.stop_flag = Event()
        super().__init__(name='Sniff Process', daemon=daemon)

    def stop_filter(self, packet):
        return self.stop_flag.is_set()

    def run(self):
        sniff(filter=self.bpf_filter, prn=self.log_packets, store=0, stop_filter=self.stop_filter)

    def log_packets(self, packet):
        if self.layers:
            if any(packet.haslayer(layer) for layer in self.layers):
                self.packets.put(packet)
        else:
            self.packets.put(packet)


class Sniffer:

    def __init__(self, bpf_filter, layers: list | tuple = (), *, daemon=False):
        self._ip_host = get_host()[1]
        self._port = get_random_port()
        self.packets = Queue()
        bpf_filter = f'({bpf_filter}) or (udp and dst host {self._ip_host} and dst port {self._port})'
        self._process = Sniff(bpf_filter, layers, self.packets, daemon=daemon)
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
        if self.running:
            raise SnifferRunningError('Stop Sniffer first.')
        with self._lock:
            self._process.start()

    def stop(self, timeout=None):
        if not self.running:
            raise SnifferRunningError('Sniffer is not running.')
        with self._lock:
            self._process.stop_flag.set()
            send_dummy_packet(local=False, payload=SENTINEL, port=self._port, verbose=False)
            self._process.join(timeout)

    def force_quit(self):
        if not self.running:
            raise SnifferRunningError('Sniffer is not running.')
        with self._lock:
            self._process.terminate()
            self._process.join()

    def reset(self):
        if self.running:
            raise SnifferRunningError('Stop Sniffer first.')
        with self._lock:
            bpf_filter, layers, daemon = self._process.bpf_filter, self._process.layers, self._process.daemon
            self.packets = Queue()
            self._process = Sniff(bpf_filter, layers, self.packets, daemon=daemon)

    def get(self, timeout=None):
        try:
            return self.packets.get(timeout=timeout)
        except Empty:
            return None


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]


if __name__ == '__main__':
    from network.layers import Raw
    from time import sleep
    sniffer = Sniffer('tcp', [Raw])
    for i in range(3):
        sniffer.start()
        sleep(3)
        sniffer.stop()
        sniffer.reset()