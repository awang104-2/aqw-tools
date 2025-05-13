from game.packets import GameSniffer
from bot.autoclicker import AutoClicker
import pynput
import pywinauto
import time


keys_pressed = []
abilities_used = []


act_reference = {'aa': '1', 'a1': '2', 'a2': '3', 'a3': '4', 'a4': '5'}


# 2256x1504
START, ENTER, EXIT, STOP, CENTER = (380, 520), (1450, 800), (1650, 1200), (380, 520), (1128, 1000)

# 1920x1080
# START, ENTER, EXIT, STOP, CENTER = (200, 350), (1200, 300), (1400, 900), (200, 350), (960, 750)

def on_release(key, sniffer):
    if key == pynput.keyboard.Key.esc:
        sniffer.stop()
        return False
    key = repr(key)[1]
    if key in ['1', '2', '3', '4', '5']:
        keys_pressed.append(key)
        if key == '4':
            keys_pressed.append('1')


def modifier_stats(minutes):
    autoclicker = AutoClicker()
    sniffer = GameSniffer('any')
    sniffer.start()
    autoclicker.click(START)
    print('started')
    time.sleep(0.5)
    autoclicker.click(CENTER)
    time.sleep(0.5)
    autoclicker.click(ENTER)
    time.sleep(1.5)
    count = 0
    start_time = time.time()
    while time.time() - start_time < 60 * minutes:
        try:
            key = str(count % 5 + 1)
            autoclicker.press(key)
            count += 1
            time.sleep(0.05)
        except pywinauto.findwindows.ElementNotFoundError as e:
            sniffer.force_quit()
            raise e
    autoclicker.click(EXIT)
    time.sleep(2)
    sniffer.stop(10)
    print('ended')
    time.sleep(0.5)
    autoclicker.click(STOP)
    time.sleep(0.5)
    autoclicker.click(CENTER)
    string = ''
    attack_data = {'hit': 0, 'miss': 0, 'crit': 0, 'dodge': 0, 'damage': 0, 'healing': 0}
    enemy_data = {'hit': 0, 'miss': 0, 'crit': 0, 'dodge': 0, 'damage': 0, 'healing': 0}
    while not sniffer.jsons.empty():
        json = sniffer.jsons.get()
        if json:
            json = json['b']['o']
            if json['cmd'] == 'ct':
                if json.get('sarsa'):
                    sarsas = json['sarsa']
                    for sarsa in sarsas:
                        datapoints = sarsa['a']
                        for datapoint in datapoints:
                            string += f'sarsa: {datapoint}\n'
                            key = datapoint.get('type')
                            if key in attack_data.keys():
                                attack_data[key] += 1
                            hp = datapoint['hp']
                            if hp >= 0:
                                attack_data['damage'] += hp
                                if hp not in [1830, 5293]:
                                    print(f'special case {hp}: {json}')
                            elif hp < 0:
                                attack_data['healing'] -= hp
                                if hp not in [-2431, -1870]:
                                    print(f'special case {hp}: {json}')

                elif json.get('sara'):
                    datapoints = json['sara']
                    for datapoint in datapoints:
                        string += f'sara: {datapoint}\n'
                        key = datapoint['actionResult'].get('type')
                        if key in enemy_data.keys():
                            enemy_data[key] += 1
                        hp = int(datapoint['actionResult']['hp'])
                        if hp > 0:
                            enemy_data['damage'] += hp
                        elif hp < 0:
                            attack_data['healing'] -= hp
    string +='\n'
    print(string)
    with open("log.txt", 'a') as file:
        file.write(string)
    total = attack_data['hit'] + attack_data['miss'] + attack_data['dodge'] + attack_data['crit']
    enemy_total = enemy_data['hit'] + enemy_data['miss'] + enemy_data['dodge'] + enemy_data['crit']
    string = f'Test:\nPlayer Crit Chance: {round(attack_data['crit'] / total * 100, 2)}%\n'
    string += f'Player Miss Chance: {round(attack_data['miss'] / total * 100, 2)}%\n'
    string += f'Player Dodge Chance: {round(enemy_data['dodge'] / enemy_total * 100, 2)}%\n'
    string += f'Player Damage: {attack_data['damage']}\n'
    string += f'Player Healing: {attack_data['healing']}\n'
    string += f'Player Total: {total}\n'
    string += f'Enemy Crit Chance: {round(enemy_data['crit'] / enemy_total * 100, 2)}%\n'
    string += f'Enemy Miss Chance: {round(enemy_data['miss'] / enemy_total * 100, 2)}%\n'
    string += f'Enemy Dodge Chance: {round(attack_data['dodge'] / total * 100, 2)}%\n'
    string += f'Enemy Damage: {enemy_data['damage']}\n'
    string += f'Enemy Healing: {enemy_data['healing']}\n'
    string += f'Enemy Total: {enemy_total}\n\n'
    print(string)
    with open("data.txt", 'a') as file:
        file.write(string)


def measure_modifier_stats(minutes):
    sniffer = GameSniffer('any')
    print('starting')
    sniffer.start()
    print('started')
    start_time = time.time()
    time.sleep(minutes * 60)
    end_time = time.time()
    print(end_time - start_time)
    print('stopping')
    sniffer.stop()
    print('stopped')
    print('packet queue size:', sniffer.packets.qsize())
    while not sniffer.jsons.empty():
        print(sniffer.jsons.get())


if __name__ == '__main__':
    count = 0
    total = 0
    sniffer = GameSniffer('any')
    autoclicker = AutoClicker()
    listener = pynput.keyboard.Listener(on_release=lambda key: on_release(key, sniffer))
    keyboard = pynput.keyboard.Controller()
    listener.start()
    sniffer.start()
    time.sleep(3)
    n = 0
    while sniffer.is_alive():
        autoclicker.press(str(n % 3 + 2))
        n += 1
        time.sleep(0.1)
        json = sniffer.get_json(block=False)
        if json:
            json = json['b']['o']
            if json.get('cmd') == 'ct':
                sarsa = json.get('sarsa')
                if sarsa:
                    for s in sarsa:
                        for a in s['a']:
                            damage = a['hp']
                            if damage >= 0:
                                total += damage
                            count += 1
                            print(count, '-', a, '|', damage, '|', total)
    print('ended')
    print(f'total damage: {total}')
    '''

    results = [
        {'hp': 1024, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': -1711, 'actRef': 'a2', 'tInf': 'p:35948', 'type': 'crit'},
        {'hp': 1674, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': -2431, 'actRef': 'a2', 'tInf': 'p:35948', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': -2431, 'actRef': 'a2', 'tInf': 'p:35948', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': -2431, 'actRef': 'a2', 'tInf': 'p:35948', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': -2431, 'actRef': 'a2', 'tInf': 'p:35948', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1024, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1288, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': -1711, 'actRef': 'a2', 'tInf': 'p:35948', 'type': 'crit'},
        {'hp': 1674, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': -2431, 'actRef': 'a2', 'tInf': 'p:35948', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a1', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 0, 'actRef': 'a3', 'tInf': 'p:35948', 'type': 'none'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 5293, 'actRef': 'a4', 'tInf': 'm:1', 'type': 'crit'},
        {'hp': 1830, 'actRef': 'aa', 'tInf': 'm:1', 'type': 'crit'},
    ]
    total = 0
    for r in results:
        damage = r['hp']
        if damage > 0:
            total += damage
            print(damage)
    print(total)
    20783
    '''