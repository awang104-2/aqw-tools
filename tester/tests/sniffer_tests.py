from packet_logger.sniffer import AqwPacketLogger
from tester.tests import current_dir
from packet_logger.aqw_info import servers
from bot.autoclicker import AutoClicker
from pynput.keyboard import Listener
from threading import Thread
from time import sleep


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
    results = packet_logger.parse_packets_to_data(save=current_dir + 'sniffer_jsons.json', include=include, exclude=exclude)
    print('')
    for dictionary in results:
        print(dictionary)
    return results


def supplies_quest_test():
    while True:
        server = input('Server > ').lower()
        if server in servers.keys():
            break
        else:
            print('Invalid server name.')
    while True:
        time = int(input('Time (s) > '))
        if isinstance(time, int) and time > 0:
            break
        else:
            print('Invalid time.')

    server = servers[server.lower()]
    packet_logger = AqwPacketLogger(server=server)
    autoclicker = AutoClicker()
    logger_thread = Thread(target=packet_logger.start)
    logger_thread.start()
    drops = 0
    for i in range(10 * time):
        if drops >= 30:
            break
        results = packet_logger.parse_packets_to_data(include=['dropItem'])
        for r in results:
            if r['items'].get('67266', None):
                drops += 1
        autoclicker.press(str(i % 5 + 1))
        sleep(0.1)
    packet_logger.stop()
    logger_thread.join()
    print(f'\nTotal drops: {drops}')



