from game.packets import GameSniffer
from bot.autoclicker import AutoClicker
import pywinauto
import time

# 2256x1504
# START, ENTER, EXIT, STOP, CENTER = (380, 520), (1450, 800), (1650, 1200), (380, 520), (1000, 800)

# 1920x1080
START, ENTER, EXIT, STOP, CENTER = (200, 350), (1200, 300), (1400, 900), (200, 350), (960, 750)


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
                        hp = int(datapoint['actionResult']['hp'])
                        if hp > 0:
                            enemy_data['damage'] += hp
                        elif hp < 0:
                            attack_data['healing'] -= hp
    print(f'Attack Data: {attack_data}')
    print(f'Enemy Data: {enemy_data}')
    total = attack_data['hit'] + attack_data['miss'] + attack_data['dodge'] + attack_data['crit']
    print(f'Enemy Dodge Chance: {attack_data['dodge'] / total}')
    print(f'Enemy Miss Chance')


if __name__ == '__main__':
    modifier_stats(10)