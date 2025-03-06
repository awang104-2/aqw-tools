from packet_logger.sniffer import AqwPacketLogger, Sniffer
from threading import Timer
from time import sleep
from time import time as get_time
from pynput.keyboard import Listener, Key


def get_bpf_filter(bpf, server):
    server = AqwPacketLogger.get_servers().get(server)
    return bpf + ' ' + server


def sniff_test(bpf_filter=None):
    if not bpf_filter:
        bpf_filter = input('BPF Filter > ').lower()

    sniffer = Sniffer(bpf_filter=bpf_filter)
    sniffer.set_concurrent_packet_summary_on(True)

    def on_release(key):
        if key == Key.esc:
            sniffer.stop()
            return False

    print('\nPress \'esc\' to exit:')
    sniffer.start()
    listener = Listener(on_release=on_release)
    listener.run()
    print('\nResults:')
    print(repr(sniffer))


def sniff_aqw_test(include=None, exclude=None):
    server = input('Server > ').lower()
    time = int(input('Time (s) > '))
    print('')

    packet_logger = AqwPacketLogger(server=server)
    packet_logger.set_concurrent_packet_summary_on(False)
    packet_logger.start()

    timer = Timer(time, packet_logger.stop)
    timer.run()

    results = packet_logger.get_jsons(include=include, exclude=exclude)
    print('\nPrinting results:')
    for i, dictionary in enumerate(results):
        print(f'{i + 1} - {dictionary}')


def drop_test():    
    drops = {}

    server = input('Server > ').lower()
    time = int(input('Time (s) > '))
    print('')

    packet_logger = AqwPacketLogger(server=server)
    packet_logger.start()

    start_time = get_time()
    while True:
        end_time = get_time()
        if end_time - start_time >= time:
            break
        results = packet_logger.get_jsons(include=['addItems', 'dropItem'])
        for data in results:
            interpret(drops, data)
        sleep(0.1)

    packet_logger.stop()

    print('\nDrops:')
    for key in drops.keys():
        print(key + ':', drops[key])


def interpret(drops, data):
    match data.get('cmd'):
        case 'dropItem' | 'addItems':
            item_num = list(data.get('items').keys())[0]
            if drops.get(item_num, None):
                drops[item_num]['count'] += data.get('items').get(item_num).get('iQty')
            else:
                num = data.get('items').get(item_num).get('iQty')
                name = data.get('items').get(item_num).get('sName', None)
                drops[item_num] = {'name': name, 'count': num}
    return drops
