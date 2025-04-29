from scapy.layers.l2 import Ether, ARP, Dot1Q
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6
from scapy.layers.dns import DNS
from scapy.layers.dot11 import Dot11
from scapy.packet import Raw, Padding
import types


LINK_LAYERS = [Ether, Dot1Q, ARP, Dot11]
NETWORK_LAYERS = [IP, IPv6]
TRANSPORT_LAYERS = [TCP, UDP, ICMP]
APPLICATION_LAYERS = [DNS]
GAME_LAYERS = [Raw, TCP, IP, Padding]


__all__ = [name for name, obj in globals().items() if not name.startswith('_') and not isinstance(obj, types.ModuleType)]