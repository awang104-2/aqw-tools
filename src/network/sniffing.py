from scapy.all import AsyncSniffer, Scapy_Exception
from queue import Queue, Empty
from decorators import *


class Sniffer:

    def __init__(self, bpf_filter, layers: list | tuple = (), summary_on=False):
        self._filter = bpf_filter
        self._layers = layers
        self._packets = Queue()
        self._sniffer = AsyncSniffer(filter=bpf_filter, prn=self.log_packet, store=0)
        self._summary_on = summary_on

    @property
    def summary_on(self):
        return self._summary_on

    @summary_on.setter
    @check_not_running
    def summary_on(self, boolean):
        self._summary_on = boolean

    @property
    def filter(self):
        return self._filter

    @property
    def layers(self):
        return self._layers

    @property
    def running(self):
        return self._sniffer.running

    @check_not_running
    def start(self):
        try:
            self._sniffer.start()
        except Scapy_Exception:
            raise RuntimeError(f'Call reset before starting {self.__name__} instance again.')

    @check_running
    def stop(self):
        self._sniffer.join(timeout=0.01)
        self._sniffer.stop()

    def put(self, packet):
        self._packets.put(packet)

    def log_packet(self, packet):
        if self._layers:
            if len(self._layers) == 1 and packet.haslayer(self._layers[0]):
                self._packets.put(packet)
                if self._summary_on:
                    return packet.summary()
            elif any(packet.haslayer(layer) for layer in self._layers):
                self._packets.put(packet)
                if self._summary_on:
                    return packet.summary()
        else:
            self._packets.put(packet)
            if self._summary_on:
                return packet.summary()

    @check_not_running
    def reset(self):
        self._packets = Queue()
        self._sniffer = AsyncSniffer(filter=self.filter, prn=self.log_packet, store=0)

    def get(self, timeout=None):
        try:
            return self._packets.get(timeout=timeout)
        except Empty:
            return None


__all__ = [name for name in globals() if not name.startswith('-')]