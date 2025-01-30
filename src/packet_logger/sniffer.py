from scapy.all import sniff, Raw
from json import loads, dumps
from queue import Queue
from threading import Event
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


class Sniffer:

    def __init__(self, bpf_filter, packet_summary=False):
        self.filter = bpf_filter
        self.packets = Queue()
        self.running = Event()
        self.stop_filter = lambda packet: not self.running.is_set()
        self.summary = packet_summary

    def start(self, time=None, count=None):
        self.running.set()
        print('Sniffing...')
        if time and count:
            sniff(filter=self.filter, prn=self.log_packet, store=0, timeout=time, count=count, stop_filter=self.stop_filter)
        elif count:
            sniff(filter=self.filter, prn=self.log_packet, store=0, count=count, stop_filter=self.stop_filter)
        elif time:
            sniff(filter=self.filter, prn=self.log_packet, store=0, timeout=time, stop_filter=self.stop_filter)
        else:
            sniff(filter=self.filter, prn=self.log_packet, store=0, stop_filter=self.stop_filter)

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

    def stop(self):
        if self.running.is_set():
            self.running.clear()


class AqwPacketLogger(Sniffer):

    def __init__(self, server):
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

