from scapy.all import sniff, Raw
from json import loads, dumps
from queue import Queue
from scapy.all import conf, get_if_addr
from threading import Event, Thread


def packet_to_str(packet):
    try:
        bytes_obj = packet[Raw].load
    except IndexError:
        return '###'
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
    raise ValueError('Incomplete or incompatible string for JSON object parsing: ' + string)


def get_dst_ip():
    return get_if_addr(conf.iface)


class Sniffer:

    def __init__(self, bpf_filter):
        self.filter = bpf_filter
        self.packets = Queue()
        self.summary = Event()
        self.summary.clear()
        self.running = Event()
        self.running.clear()
        self.sniff_thread = None

    def set_bpf_filter(self, bpf_filter):
        self.filter = bpf_filter

    def start(self):
        self.sniff_thread = Thread(target=self.run, daemon=True)
        self.sniff_thread.start()

    def run(self):
        self.sniff_thread = Thread(target=self.sniff)
        self.sniff_thread.run()

    def stop(self, join=False):
        if self.running.is_set():
            if join:
                self.sniff_thread.join()
            self.running.clear()

    def sniff(self):
        self.running.set()
        print('Sniffing...')
        sniff(filter=self.filter, prn=self.log_packet, store=0, stop_filter=lambda x: not self.running.is_set())

    def __repr__(self):
        buffer = ''
        while not self.packets.empty():
            p = self.packets.get()
            buffer += packet_to_str(p)
        return buffer

    def __str__(self):
        buffer = ''
        k = 0
        while not self.packets.empty():
            k += 1
            p = self.packets.get()
            buffer += str(k) + ' - ' + packet_to_str(p) + '\n'
        return buffer

    def set_concurrent_packet_summary_on(self, status):
        if status:
            self.summary.set()
        else:
            self.summary.clear()

    def log_packet(self, packet):
        self.packets.put(packet)
        if self.summary.is_set():
            print(packet.summary())



class AqwPacketLogger(Sniffer):

    aqw_servers = {
        "artix": "172.65.160.131",
        "swordhaven": "172.65.207.70",
        "yokai": "172.65.236.72",
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

    @staticmethod
    def get_servers():
        return AqwPacketLogger.aqw_servers.copy()

    def __init__(self, server):
        server = self.aqw_servers.get(server, server)
        super().__init__(f'tcp and src host {server}')

    def log_packet(self, packet):
        if packet.haslayer(Raw):
            super().log_packet(packet=packet)

    def set_server(self, server):
        server = self.aqw_servers.get(server, server)
        bpf_filter = f'tcp and src host {server}'
        super().set_bpf_filter(bpf_filter)

    def parse_packets_to_data(self, include=None, exclude=None, save=None):

        if include and exclude:
            raise ValueError('Cannot specify both \'include\' and \'exclude\'.')

        buffer = repr(self)
        dataset = []

        while True:
            try:
                json_string, buffer = str_to_json(buffer)
                entry = loads(json_string)['b']['o']
                if not (include or exclude) or (include and entry.get('cmd', '') in include) or (exclude and not entry.get('cmd', '') in exclude):
                    dataset.append(entry)
            except ValueError:
                if save:
                    with open(save, "w") as outfile:
                        for e in dataset:
                            outfile.write(dumps(e) + '\n')
                return dataset

    def print_packets_as_data(self, include=None, exclude=None):
        results = self.parse_packets_to_data(include=include, exclude=exclude)
        print('\nPrinting results:')
        for i, dictionary in enumerate(results):
            print(f'{i + 1} - {dictionary}')

