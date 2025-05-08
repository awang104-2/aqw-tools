from game.packets import GameSniffer
from bot.autoclicker import AutoClicker
import multiprocessing
import pywinauto
import time


START, ENTER, EXIT, STOP, CENTER = (380, 520), (1450, 800), (1650, 1200), (380, 520), (1000, 800)


def modifier_stats():
    autoclicker = AutoClicker()
    autoclicker.click(START)
    sniffer = GameSniffer('any')
    sniffer.start()
    print('started')
    time.sleep(3)
    autoclicker.click(ENTER)
    time.sleep(5)
    start_time = time.time()
    while time.time() - start_time < 60 * 10:
        for i in range(60 * 10 * 10):
            try:
                key = str(i % 5 + 1)
                autoclicker.press(key)
                time.sleep(0.05)
            except pywinauto.findwindows.ElementNotFoundError as e:
                sniffer.force_quit()
                raise e
    autoclicker.click(EXIT)
    time.sleep(5)
    sniffer.stop()
    print('ended')
    time.sleep(3)
    autoclicker.click(STOP)
    time.sleep(0.5)
    autoclicker.click(CENTER)
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
                            key = datapoint.get('type')
                            if key in attack_data.keys():
                                attack_data[key] += 1
                            hp = datapoint['hp']
                            if hp > 0:
                                attack_data['damage'] += hp
                            elif hp < 0:
                                attack_data['healing'] -= hp
                elif json.get('sara'):
                    datapoints = json['sara']
                    for datapoint in datapoints:
                        key = datapoint['actionResult'].get('type')
                        if key in enemy_data.keys():
                            enemy_data[key] += 1
                        hp = datapoint['actionResult']['hp']
                        if hp > 0:
                            enemy_data['damage'] += hp
                        elif hp < 0:
                            enemy_data['damage'] -= hp
    print(f'Attack Data: {attack_data}')
    print(f'Enemy Data: {enemy_data}')


if __name__ == '__main__':
    modifier_stats()