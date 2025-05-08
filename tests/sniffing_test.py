from tests.monitor import monitor
from network.sniffing import Sniffer
from game.packets import GameSniffer
import time
import random


def measure_ram_cpu(sniffer, interval, logs):
    sniffer.reset()
    print('Testing RAM and CPU usage.')
    print('Test started.')
    start_time = time.time()
    sniffer.start()
    result = monitor(interval, logs)
    sniffer.stop()
    end_time = time.time()
    print('Test ended.')
    print(f'Test Duration: {end_time - start_time}s')
    print(f'Results:\n{result}')


def test_reset(sniffer):
    sniffer.reset()
    print('Testing reset method.')
    print('Test started.')
    start_time = time.time()
    for i in range(3):
        try:
            print(f'Trial {i + 1} started.')
            sniffer.start()
            time.sleep(3)
            sniffer.stop()
            sniffer.reset()
            print(f'Trial {i + 1} completed.')
        except Exception as e:
            print(f'Trial {i + 1} failed: {e}')
    end_time = time.time()
    print('Test ended.')
    print(f'Test Duration: {end_time - start_time}s\n')


def test_errors(sniffer):
    sniffer.reset()
    print('Testing for errors.')
    print('Test started.')
    try:
        sniffer.start()
        sniffer.start()
    except Exception as e:
        print(f'Error Detected: {e}')
    try:
        sniffer.reset()
    except Exception as e:
        print(f'Error Detected: {e}')
    try:
        sniffer.stop()
        sniffer.stop()
    except Exception as e:
        print(f'Error Detected: {e}')
    print('Test ended.')


def json_sniffing():
    import time
    from bot.autoclicker import AutoClicker
    autoclicker = AutoClicker()
    autoclicker.connect()
    sniffer = GameSniffer('any')
    sniffer.start()
    print('started')
    for i in range(3000):
        key = str(i % 4 + 2)
        autoclicker.press(key)
    sniffer.stop()
    print('ended')
    attack_data = {'hit': 0, 'miss': 0, 'crit': 0, 'dodge': 0, 'damage': 0}
    while not sniffer.jsons.empty():
        json = sniffer.jsons.get()
        if json:
            json = json['b']['o']
            if json['cmd'] == 'ct' and json.get('sarsa'):
                datapoint = json['sarsa'][0]['a'][0]
                key = datapoint.get('type')
                if attack_data.get(key):
                    attack_data[key] += 1
                attack_data['damage'] += max(datapoint['hp'], 0)
    print(attack_data)


if __name__ == '__main__':
    json_sniffing()
