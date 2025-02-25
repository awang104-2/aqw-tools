from bot.autoclicker import AutoClicker
from packet_logger.sniffer import AqwPacketLogger
from time import time as get_time, sleep
from threading import Timer
from handlers.DataHandler import add_data_to_csv
from tkinter import Label, Button, Tk


def popup_window():
    window = Tk()
    window.attributes('-topmost', True)
    label = Label(window, text="Testing finished.")
    label.pack(fill='x')
    button_close = Button(window, text="Ok", command=window.destroy)
    button_close.pack(side='bottom', pady=10)
    geometry = '150x80+' + str(int(window.winfo_screenwidth() / 2) - 75) + '+' + str(int(window.winfo_screenheight() / 2) - 80)
    print(geometry)
    window.geometry(geometry)
    window.mainloop()


def combat_loop(packet_logger, combo=('1', '2', '3', '4', '5')):
    while packet_logger.is_running():
        autoclicker = AutoClicker()
        for key in combo:
            autoclicker.press(key)
            sleep(0.1)


def sample(server, time, combo):
    packet_logger = AqwPacketLogger(server=server)
    packet_logger.set_concurrent_packet_summary_on(False)
    packet_logger.start()
    start = get_time()
    timer = Timer(time, packet_logger.stop)
    timer.start()
    combat_loop(packet_logger, combo)
    end = get_time()
    return packet_logger, (end - start)


def get_player_data(packet_logger, count):
    player_total, player_hit, player_crit, player_dodge, player_miss = (0, 0, 0, 0, 0)
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
        if player_total == count:
            break
    return {'hit': [player_hit], 'crit': [player_crit], 'dodge': [player_dodge], 'miss': [player_miss], 'total': [player_total], 'p': [player_crit / player_total]}


def get_monster_data(packet_logger, count):
    monster_total, monster_hit, monster_crit, monster_dodge, monster_miss = (0, 0, 0, 0, 0)
    results = packet_logger.get_jsons(include=['ct'])
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
        if monster_total == count:
            break
    return {'hit': [monster_hit], 'crit': [monster_crit], 'dodge': [monster_dodge], 'miss': [monster_miss], 'total': [monster_total], 'p': [monster_crit / monster_total]}


def get_data(lvl, cls, pexp, server, time, combo, count):
    packet_logger, time = sample(server, time, combo)
    p_data = get_player_data(packet_logger, count)
    p_data['level'], p_data['class'], p_data['pexp'] = lvl, cls, pexp
    return p_data


def run_test(lvl, cls, pexp, server, time, combo, count, filename, location):
    data = get_data(lvl, cls, pexp, server, time, combo, count)
    add_data_to_csv(filename, location, data)


if __name__ == '__main__':
    lvl = 100
    cls = 'lightcaster'
    pexp = 0.4933
    server = 'twig'
    time = 300
    combo = ['2', '5']
    count = 2000
    filename = 'combat_sample_data.csv'
    location = '../../tester/tests'
    run_test(lvl, cls, pexp, server, time, combo, count, filename, location)
    popup_window()



'''
print(f'\nTime Passed: {round(end - start, 2)}s')
print('\n-------Player-------')
print('Total:', player_total)
print('Hit:', player_hit)
print('Crit:', player_crit)
print('Dodge:', player_dodge)
print('Miss:', player_miss)
print('**Probability**')
print('Crit:', player_crit / player_total)
print('Dodge:', player_dodge / player_total)
print('Miss:', player_miss / player_total)
print('-------Monster-------')
print('Total:', monster_total)
print('Hit:', monster_hit)
print('Crit:', monster_crit)
print('Dodge:', monster_dodge)
print('Miss:', monster_miss)
print('**Probability**')
print('Crit:', monster_crit / monster_total)
print('Dodge:', monster_dodge / monster_total)
print('Miss:', monster_miss / monster_total)
print('')
'''
