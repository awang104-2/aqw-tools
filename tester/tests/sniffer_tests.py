from packet_logger.sniffer import AqwPacketLogger, Sniffer
from threading import Timer
from time import sleep
from time import time as get_time
from pynput.keyboard import Listener, Key
from bot.autoclicker import AutoClicker
from tkinter import Label, Button, Tk


def popup_window():
    window = Tk()
    window.attributes('-topmost', True)
    label = Label(window, text="Testing finished.")
    label.pack(fill='x', padx=50, pady=5)
    button_close = Button(window, text="Ok", command=window.destroy)
    button_close.pack(fill='x')
    window.mainloop()


def combat_loop(packet_logger, combo=('1', '2', '3', '4', '5')):
    while packet_logger.is_running():
        autoclicker = AutoClicker()
        for key in combo:
            autoclicker.press(key)
            sleep(0.1)

def combat_sample_test():
    server = input('Server > ').lower()
    time = int(input('Time (s) > '))
    auto_combat = input('Yes or No > ').lower()
    match auto_combat:
        case 'yes':
            auto_combat = True
            combo = tuple(input('Combo, split with commas > ').split(','))
        case 'no':
            auto_combat = False
    print('')

    packet_logger = AqwPacketLogger(server=server)
    packet_logger.set_concurrent_packet_summary_on(False)
    packet_logger.start()

    timer = Timer(time, packet_logger.stop)
    if auto_combat:
        timer.start()
        combat_loop(packet_logger, combo)
    else:
        timer.run()

    player_total = 0
    player_hit = 0
    player_crit = 0
    player_dodge = 0
    player_miss = 0
    monster_total = 0
    monster_hit = 0
    monster_crit = 0
    monster_dodge = 0
    monster_miss = 0

    results = packet_logger.get_jsons(include=['ct'])
    for result in results:
        infos = result.get('sarsa', None)
        if not infos:
            continue
        else:
            infos = infos[0].get('a')
        for info in infos:
            hit_type = info.get('type')
            if hit_type == 'hit':
                player_hit += 1
                player_total += 1
            elif hit_type == 'crit':
                player_crit += 1
                player_total += 1
            elif hit_type == 'dodge':
                player_dodge += 1
                player_total += 1
            elif hit_type == 'miss':
                player_miss += 1
                player_total += 1
    for result in results:
        infos = result.get('sara')
        if not infos:
            continue
        for info in infos:
            hit_type = info.get('actionResult').get('type')
            match hit_type:
                case 'hit':
                    monster_hit += 1
                    monster_total += 1
                case 'crit':
                    monster_crit += 1
                    monster_total += 1
                case 'dodge':
                    monster_dodge += 1
                    monster_total += 1
                case 'miss':
                    monster_miss += 1
                    monster_total += 1
    print('\n-------Player-------')
    print('Total:', player_total)
    print('Hit:', player_hit)
    print('Crit:', player_crit)
    print('Dodge:', player_dodge)
    print('Miss:', player_miss)
    print('\nProbability:')
    print('Crit:', player_crit / player_total)
    print('Dodge:', player_dodge / player_total)
    print('Miss:', player_miss / player_total)
    print('\n\n-------Monster-------')
    print('Total:', monster_total)
    print('Hit:', monster_hit)
    print('Crit:', monster_crit)
    print('Dodge:', monster_dodge)
    print('Miss:', monster_miss)
    print('\nProbability:')
    print('Crit:', monster_crit / monster_total)
    print('Dodge:', monster_dodge / monster_total)
    print('Miss:', monster_miss / monster_total)


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


if __name__ == '__main__':
    # sniff_aqw_test()
    combat_sample_test()
    popup_window()
