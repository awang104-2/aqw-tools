from scapy.all import send
from scapy.layers.inet import IP, TCP
import numpy as np


PRIVATE_PORT = 51272


def send_dummy_packet(verbose=False):
    pkt = IP(dst="127.0.0.1") / TCP(dport=51272, flags="S")
    send(pkt, verbose=verbose)


def get_random_private_port():
    return int(np.random.rand() * 20000 + 40000)


__all__ = [name for name in globals() if not name.startswith('-')]