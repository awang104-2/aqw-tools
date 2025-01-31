from scapy.all import AsyncSniffer, Raw
from json import loads, dumps
from queue import Queue
from scapy.all import conf, get_if_addr


def packet_to_str(packet):
    bytes_obj = packet[Raw].load
    if len(bytes_obj) < 15000:
        string = bytes_obj.decode('utf-8')
    else:
        string = ''
    return string


def str_to_json(string):
    raw_data = string
    start, end, bracket_count = (0, 0, 0)
    for i, char in enumerate(raw_data):
        if char == '{':
            if bracket_count == 0:
                start = i
            bracket_count += 1
        elif char == '}':
            bracket_count -= 1
            if bracket_count == 0:
                end = i
                return string[start:end + 1], string[end + 1:]
    raise ValueError('Incomplete or incompatible string for JSON object parsing.')


def get_dst_ip():
    return get_if_addr(conf.iface)


class Sniffer(AsyncSniffer):

    def __init__(self, bpf_filter, packet_summary=False):
        self.filter = bpf_filter
        self.packets = Queue()
        self.summary = packet_summary
        super().__init__(filter=self.filter, prn=self.log_packet, store=0)

    def start(self):
        print('Sniffing...')
        super().start()

    def __str__(self):
        buffer = ''
        while not self.packets.empty():
            p = self.packets.get()
            buffer += packet_to_str(p)
        return buffer

    def set_concurrent_packet_summary_on(self, status):
        self.summary = status

    def log_packet(self, packet, has_raw):
        if has_raw and not packet.haslayer(Raw):
            pass
        else:
            self.packets.put(packet)
            if self.summary:
                print(packet.summary())



class AqwPacketLogger(Sniffer):

    aqw_servers = {
        "artix": "172.65.160.131",
        "swordhaven (EU)": "172.65.207.70",
        "yokai (SEA)": "172.65.236.72",
        "yorumi": "172.65.249.41",
        "twilly": "172.65.210.123",
        "safiria": "172.65.249.3",
        "galanoth": "172.65.249.3",
        "alteon": "172.65.235.85",
        "gravelyn": "172.65.235.85",
        "twig": "172.65.235.85",
        "sir ver": "172.65.220.106",
        "espada": "172.65.220.106",
        "sepulchure": "172.65.220.106"
    }

    def __init__(self, server):
        server = self.aqw_servers.get(server, server)
        super().__init__(f'tcp and src host {server}', packet_summary=False)

    def log_packet(self, packet):
        super().log_packet(packet=packet, has_raw=True)

    def parse_packets_to_data(self, include=None, exclude=None, save=None):

        if include and exclude:
            raise ValueError("Cannot specify both 'include' and 'exclude'.")

        buffer = str(self)
        data = []

        while True:
            try:
                json_string, buffer = str_to_json(buffer)
                entry = loads(json_string)['b']['o']
                if not (include or exclude) or (include and entry.get('cmd', '') in include) or (exclude and not entry.get('cmd', '') in exclude):
                    data.append(entry)
            except ValueError:
                if save:
                    with open(save, "w") as outfile:
                        for e in data:
                            outfile.write(dumps(e) + '\n')
                return data

