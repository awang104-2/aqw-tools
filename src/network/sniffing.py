from scapy.all import sniff
from multiprocessing import Process, Queue
from queue import Empty


class SnifferRunningError(RuntimeError):

    def __init__(self, msg):
        super().__init__(msg)


class Sniff(Process):

    def __init__(self, bpf_filter, layers, queue):
        self.bpf_filter = bpf_filter
        self.layers = layers
        self.packets = queue
        super().__init__(name='Sniff Process')

    def run(self):
        print('Sniffing...')
        sniff(filter=self.bpf_filter, prn=self.log_packets, store=0)

    def log_packets(self, packet):
        if self.layers:
            if len(self.layers) == 1 and packet.haslayer(self.layers[0]):
                self.packets.put(packet)
            elif any(packet.haslayer(layer) for layer in self.layers):
                self.packets.put(packet)
        else:
            self.packets.put(packet)


class Sniffer:

    def __init__(self, bpf_filter, layers: list | tuple = ()):
        self.packets = Queue()
        self._process = Sniff(bpf_filter, layers, self.packets)

    @property
    def filter(self):
        return self._process.bpf_filter

    @property
    def layers(self):
        return self._process.layers

    @property
    def running(self):
        return self._process.is_alive()

    def start(self):
        self._process.start()

    def stop(self):
        self._process.terminate()
        self._process.join()

    def reset(self):
        if self._process.is_alive():
            raise SnifferRunningError('Cannot reset while Sniffer is running.')
        bpf_filter, layers = self._process.bpf_filter, self._process.layers
        self.packets = Queue()
        self._process = Sniff(bpf_filter, layers, self.packets)

    def get(self, timeout=None):
        try:
            return self.packets.get(timeout=timeout)
        except Empty:
            return None

    def join(self, timeout=None):
        self._process.join(timeout)


__all__ = [name for name in globals() if not name.startswith('-')]
