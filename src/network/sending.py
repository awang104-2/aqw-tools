from scapy.layers.inet import IP, TCP, UDP, Ether
from scapy.all import conf, send, Raw, get_if_list, get_if_hwaddr, get_working_if, sendp
import numpy as np
import socket
import types



DEFAULT_PORT = 51272
LOOPBACK_IP = "127.0.0.1"


def send_dummy(local, port=DEFAULT_PORT, payload=None, verbose=False):
    if local:
        ip_address = LOOPBACK_IP
        pkt = IP(dst=ip_address) / UDP(dport=port, flags="S")
        if payload:
            pkt = pkt / Raw(load=payload)
        send(pkt, verbose=verbose)
    else:
        iface = get_working_iface()
        ip_address = get_host()[1]
        mac = get_mac(iface)
        pkt = Ether(dst=mac) / IP(dst=ip_address, ttl=1) / UDP(dport=port, sport=port)
        if payload:
            pkt = pkt / Raw(load=payload)
        sendp(pkt, iface=iface, verbose=verbose)


def get_random_port():
    return np.random.randint(40000, 60000)


def get_host():
    host_name = socket.gethostname()
    ip_address = socket.gethostbyname(host_name)
    return host_name, ip_address


def get_mac(iface):
    dst_mac = get_if_hwaddr(iface)
    return dst_mac


def get_working_iface():
    return get_working_if()


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]