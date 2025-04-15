from scapy.all import sniff
from multiprocessing import Process, Queue
from queue import Empty
from debug.logger import Logger


class SnifferRunningError(RuntimeError):

    def __init__(self, msg):
        super().__init__(msg)


class Sniff(Process):

    def __init__(self, bpf_filter, layers, queue, *, daemon=False, log=False):
        self.bpf_filter = bpf_filter
        self.layers = layers
        self.packets = queue
        self.packet_count = 0
        self.log = log
        super().__init__(name='Sniff Process', daemon=daemon)

    def run(self):
        logger = None
        if self.log:
            logger = Logger('sniffer.txt')
            logger.clear()
            logger.info('Started sniffing.')
        sniff(filter=self.bpf_filter, prn=lambda packet: self.log_packets(packet, logger), store=0)

    def log_packets(self, packet, logger):
        if self.layers:
            if len(self.layers) == 1 and packet.haslayer(self.layers[0]):
                self.packet_count += 1
                self.packets.put(packet)
                if logger:
                    logger.info(f'Received Packet-{self.packet_count}: {packet}')
            elif any(packet.haslayer(layer) for layer in self.layers):
                self.packet_count += 1
                self.packets.put(packet)
                if logger:
                    logger.info(f'Received Packet-{self.packet_count}: {packet}')
        else:
            self.packet_count += 1
            self.packets.put(packet)
            if logger:
                logger.info(f'Received Packet-{self.packet_count}: {packet}')


class Sniffer:

    def __init__(self, bpf_filter, layers: list | tuple = (), *, daemon=False):
        self.packets = Queue()
        self._process = Sniff(bpf_filter, layers, self.packets, daemon=daemon, log=True)

    @property
    def filter(self):
        return self._process.bpf_filter

    @property
    def layers(self):
        return self._process.layers

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
        self._process.start()

    def stop(self):
        self._process.terminate()
        self._process.join()

    def reset(self):
        if self._process.is_alive():
            raise SnifferRunningError('Cannot reset while Sniffer is running.')
        bpf_filter, layers = self._process.bpf_filter, self._process.layers
        self.packets = Queue()
        self._process = Sniff(bpf_filter, layers, self.packets, daemon=self._process.daemon, log=self._process.log)

    def get(self, timeout=None):
        try:
            return self.packets.get(timeout=timeout)
        except Empty:
            return None

    def join(self, timeout=None):
        self._process.join(timeout)


__all__ = [name for name in globals() if not name.startswith('-')]
