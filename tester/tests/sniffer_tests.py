from packet_logger.sniffer import AqwPacketLogger
from tester.tests import current_dir
from packet_logger.aqw_info import servers
from threading import Thread
from time import sleep
from time import time as get_time


def sniff_test(server=None, time=None, include=None, exclude=None):
    if not server:
        while True:
            server = input('Server > ').lower()
            if server in servers.keys():
                break
            else:
                print('Invalid server name.')
    elif server.lower() not in servers:
        raise ValueError('Must be a valid server name.')

    if not time:
        while True:
            time = float(input('Time (s) > '))
            if isinstance(time, float) and time > 0:
                break
            else:
                print('Invalid time.')
    elif not isinstance(time, float) and time > 0:
        raise ValueError('Time must be an int or float.')

    server = servers[server.lower()]
    packet_logger = AqwPacketLogger(server=server)
    packet_logger.set_concurrent_packet_summary_on(True)
    packet_logger.start(time=time)
    results = packet_logger.parse_packets_to_data(save=current_dir + '\\logs\\' + 'sniffer_jsons.json', include=include, exclude=exclude)
    print('')
    for dictionary in results:
        print(dictionary)
    return results


def drop_test():
    drops = {}

    while True:
        server = input('Server > ').lower()
        if server in servers.keys():
            server = servers[server.lower()]
            break
        else:
            print('Invalid server name.')
    while True:
        time = int(input('Time (s) > '))
        if isinstance(time, int) and time > 0:
            break
        else:
            print('Invalid time.')

    packet_logger = AqwPacketLogger(server=server)
    logger_thread = Thread(target=packet_logger.start, daemon=True)
    logger_thread.start()

    start_time = get_time()
    while True:
        end_time = get_time()
        if end_time - start_time >= time:
            break
        results = packet_logger.parse_packets_to_data(include=['addItems', 'dropItem'])
        for data in results:
            interpret(drops, data)
        sleep(0.1)

    packet_logger.stop()
    logger_thread.join()

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


drop_test()


