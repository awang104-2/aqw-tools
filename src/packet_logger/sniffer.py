from scapy.all import sniff, Raw
from json import loads, dumps
from queue import Queue
from threading import Event, Thread
from packet_logger.config.aqw_info import *
from time import sleep


def get_raw(packet):
    try:
        return packet[Raw].load
    except IndexError:
        return ''

def parse_bytes(bytes_obj, limit=200):
    if bytes_obj == '':
        return []
    if len(bytes_obj) < limit:
        return [bytes_obj]
    else:
        first_half = [bytes_obj[:limit]]
        second_half = bytes_obj[limit:]
        return first_half + parse_bytes(second_half)


def decode(bytes_list, code='utf-8'):
    str_list = []
    for b in bytes_list:
        str_list.append(b.decode(code))
    return str_list


class Sniffer:

    def __init__(self, bpf_filter):
        self.filter = bpf_filter
        self.packets = Queue()
        self.summary = Event()
        self.running = Event()
        self.sniff_thread = None
        self.__receiving_packet = Event()

    def set_bpf_filter(self, bpf_filter):
        self.filter = bpf_filter

    def start(self):
        self.sniff_thread = Thread(target=self.run, daemon=True)
        self.sniff_thread.start()

    def run(self):
        self.running.set()
        self.sniff_thread = Thread(target=self.sniff)
        self.sniff_thread.run()
        self.running.clear()

    def stop(self, join=False):
        if self.running.is_set():
            if join:
                self.sniff_thread.join()
            self.running.clear()

    def sniff(self):
        print('Sniffing...')
        sniff(filter=self.filter, prn=self.log_packet, store=0, stop_filter=lambda x: not self.running.is_set())

    def set_concurrent_packet_summary_on(self, status):
        if status:
            self.summary.set()
        else:
            self.summary.clear()

    def log_packet(self, packet):
        self.__receiving_packet.set()
        self.packets.put(packet)
        if self.summary.is_set():
            print(packet.summary())
        self.__receiving_packet.clear()

    def wait_for_packet(self, timeout=None):
        self.__receiving_packet.wait(timeout)

    def is_running(self):
        return self.running.is_set()

    def reset(self):
        self.packets = Queue()
        self.summary = Event()
        self.running = Event()
        self.__receiving_packet = Event()
        self.sniff_thread = None


class AqwPacketLogger(Sniffer):

    aqw_servers = servers
    packet_types = packet_types

    @staticmethod
    def get_servers():
        return AqwPacketLogger.aqw_servers.copy()

    def __init__(self, server):
        server = self.aqw_servers.get(server, server)
        super().__init__(f'tcp and src host {server}')
        self.buffer = ''

    def __update_buffer(self):
        while not self.packets.empty():
            raw = get_raw(self.packets.get())
            blist = parse_bytes(raw)
            slist = decode(blist)
            for s in slist:
                self.buffer += s

    def __reset_buffer(self):
        self.buffer = ''

    def __parse_buffer(self):
        start, end, start_bracket_count, end_bracket_count = (0, 0, 0, 0)
        for i, char in enumerate(self.buffer):
            if char == '{':
                if start_bracket_count == 0:
                    start = i
                start_bracket_count += 1
            elif char == '}':
                end_bracket_count += 1
                if start_bracket_count == end_bracket_count != 0:
                    end = i
                    result, self.buffer = self.buffer[start:end + 1], self.buffer[end + 1:]
                    return result
        raise ValueError('Incomplete or incompatible string for JSON object parsing: ' + self.buffer)

    def reset(self):
        super().reset()
        self.__reset_buffer()

    def log_packet(self, packet):
        if packet.haslayer(Raw):
            super().log_packet(packet=packet)

    def set_server(self, server):
        server = self.aqw_servers.get(server, server)
        bpf_filter = f'tcp and src host {server}'
        super().set_bpf_filter(bpf_filter)

    def get_jsons(self, include=None, exclude=None, save=None):

        if include and exclude:
            raise ValueError('Cannot specify both \'include\' and \'exclude\'.')

        self.__update_buffer()
        dataset = []

        while True:
            try:
                json_string = self.__parse_buffer()
                entry = loads(json_string)['b']['o']
                if not (include or exclude) or (include and entry.get('cmd', '') in include) or (exclude and not entry.get('cmd', '') in exclude):
                    dataset.append(entry)
            except ValueError:
                if save:
                    with open(save, "w") as outfile:
                        for e in dataset:
                            outfile.write(dumps(e) + '\n')
                return dataset


    def print_jsons(self, include=None, exclude=None):
        results = self.get_jsons(include=include, exclude=exclude)
        print('\nPrinting results:')
        for i, dictionary in enumerate(results):
            print(f'{i + 1} - {dictionary}')


class Interpreter:

    def __init__(self, player, logger, delay=None):
        self.logger = logger
        self.player = player
        self.__running = Event()
        self.interpret_thread = None
        self.printing = Event()
        self.delay = delay

    def set_delay(self, delay):
        if not self.is_running():
            self.delay = delay

    def clear_delay(self):
        if not self.is_running():
            self.delay = None


    def interpret(self, printing):
        dataset = self.logger.get_jsons()
        for data in dataset:
            cmd = data.get('cmd')
            match cmd:
                case 'addItems' | 'dropItem':
                    if printing:
                        print(data)

    def __interpret_packets_loop(self):
        while self.logger.is_running() and self.is_running():
            if not self.delay:
                self.logger.wait_for_packet()
                self.interpret(self.printing.is_set())
            else:
                self.interpret(self.printing.is_set())
                sleep(self.delay)

    def set_printing(self, status):
        if status:
            self.printing.set()
        else:
            self.printing.clear()

    def is_running(self):
        return self.__running.is_set()

    def run(self):
        self.__running.set()
        self.__interpret_packets_loop()
        self.__running.clear()

    def start(self):
        self.interpret_thread = Thread(target=self.run)
        self.interpret_thread.start()

    def stop(self):
        self.__running.clear()
