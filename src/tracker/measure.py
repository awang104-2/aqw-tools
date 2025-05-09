from game.packets import GameSniffer
from bot.autoclicker import AutoClicker
import pywinauto
import time

# 2256x1504
START, ENTER, EXIT, STOP, CENTER = (380, 520), (1450, 800), (1650, 1200), (380, 520), (1128, 1000)

# 1920x1080
# START, ENTER, EXIT, STOP, CENTER = (200, 350), (1200, 300), (1400, 900), (200, 350), (960, 750)


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
            string += f'json: {json}\n'
            json = json['b']['o']
            if json['cmd'] == 'ct':
                if json.get('sarsa'):
                    sarsas = json['sarsa']
                    for sarsa in sarsas:
                        string += f'sarsa: {sarsa}\n'
                        datapoints = sarsa['a']
                        for datapoint in datapoints:
                            string += f'datapoint: {datapoint}\n'
                            key = datapoint.get('type')
                            if key in attack_data.keys():
                                attack_data[key] += 1
                            hp = datapoint['hp']
                            if hp >= 0:
                                attack_data['damage'] += hp
                            elif hp < 0:
                                attack_data['healing'] -= hp
                elif json.get('sara'):
                    datapoints = json['sara']
                    string += f'sara: {datapoints}'
                    for datapoint in datapoints:
                        string += f'datapoint: {datapoint}\n'
                        key = datapoint['actionResult'].get('type')
                        if key in enemy_data.keys():
                            enemy_data[key] += 1
                        hp = int(datapoint['actionResult']['hp'])
                        if hp > 0:
                            enemy_data['damage'] += hp
                        elif hp < 0:
                            attack_data['healing'] -= hp
    string +='\n'
    with open("log.txt", 'a') as file:
        file.write(string)
    total = attack_data['hit'] + attack_data['miss'] + attack_data['dodge'] + attack_data['crit']
    enemy_total = enemy_data['hit'] + enemy_data['miss'] + enemy_data['dodge'] + enemy_data['crit']
    string = f'\nPlayer Crit Chance: {round(attack_data['crit'] / total * 100, 2)}%\n'
    string += f'Player Miss Chance: {round(attack_data['miss'] / total * 100, 2)}%\n'
    string += f'Player Dodge Chance: {round(enemy_data['dodge'] / enemy_total * 100, 2)}%\n'
    string += f'Player Damage: {attack_data['damage']}\n'
    string += f'Player Healing: {attack_data['healing']}\n'
    string += f'Player Total: {total}\n'
    string += f'\nEnemy Crit Chance: {round(enemy_data['crit'] / enemy_total * 100, 2)}%\n'
    string += f'Enemy Miss Chance: {round(enemy_data['miss'] / enemy_total * 100, 2)}%\n'
    string += f'Enemy Dodge Chance: {round(attack_data['dodge'] / total * 100, 2)}%\n'
    string += f'Enemy Damage: {enemy_data['damage']}\n'
    string += f'Enemy Healing: {enemy_data['healing']}\n'
    string += f'Enemy Total: {enemy_total}\n\n'
    with open("data.txt", 'a') as file:
        file.write(string)


if __name__ == '__main__':
    modifier_stats(1)