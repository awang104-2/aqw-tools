from scapy.all import sniff, Raw
from queue import Queue
from threading import Event, Thread


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
        self.__receiving_packet = Event()
        self.__sniff_thread = Thread(target=self.sniff, name='sniff thread')

    def set_bpf_filter(self, bpf_filter):
        self.filter = bpf_filter

    def start(self):
        self.__sniff_thread.daemon = True
        self.__sniff_thread.start()

    def run(self):
        self.__sniff_thread.run()

    def stop(self):
        self.running.clear()

    def sniff(self):
        self.running.set()
        print('Sniffing...')
        sniff(filter=self.filter, prn=self.log_packet, store=0, stop_filter=lambda x: not self.running.is_set())
        self.running.clear()

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
        self.__sniff_thread = Thread(target=self.sniff, name='sniff thread')





