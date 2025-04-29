from game.updater import GameSniffer
from network.processing import Processor


game_sniffer = GameSniffer(server='twig', stop_filter='dummy')
processor = Processor(game_sniffer)
undistorted = []
distorted = []


def start_processor():
    game_sniffer.start()
    processor.start()


def stop_processor():
    game_sniffer.stop()
    processor.stop()



def print_live():
    start_processor()
    num = 0
    try:
        while num < 15:
            json = processor.get()
            if json:
                num += 1
                try:
                    extracted_json = json['b']['o']
                    undistorted.append(extracted_json)
                    print(f'{num} - {extracted_json}')
                except KeyError:
                    distorted.append(json)
    finally:
        processor.stop()
        processor.join()
        game_sniffer.stop()


def print_():
    start_processor()
    num = 0
    try:
        while num < 15:
            json = processor.get()
            if json:
                num += 1
                try:
                    extracted_json = json['b']['o']
                    undistorted.append(extracted_json)
                    # print(f'{num} - {extracted_json}')
                except KeyError:
                    distorted.append(json)
    finally:
        processor.stop()
        processor.join()
        game_sniffer.stop()


def record_and_print():
    start_processor()
    num = 0
    for i in range(300):
        json = processor.get(0.1)
        if json:
            num += 1
            print(f'json recorded #{num}')
            try:
                extracted_json = json['b']['o']
                undistorted.append(extracted_json)
            except KeyError:
                distorted.append(json)
    processor.stop()
    processor.join()
    game_sniffer.stop()
    print('\n\nUndistorted:')
    for i, json in enumerate(undistorted):
        print(f'{i + 1} - {json}')
    print('\nDistorted:')
    for i, json in enumerate(distorted):
        print(f'{i + 1} - {json}')


def print_skills():
    start_processor()
    try:
        while True:
            json = processor.get()
            json = json['b']['o']
            if json.get('cmd') == 'sAct':
                print('-----------Active-----------')
                for i, skill in enumerate(json['actions']['active']):
                    print(f'Skill #{i + 1}')
                    for key, value in skill.items():
                        print(f'{key}: {value}')
                    print()
                print('-----------Passive-----------')
                for i, skill in enumerate(json['actions']['passive']):
                    print(f'Passives #{i + 1}')
                    for key, value in skill.items():
                        print(f'{key}: {value}')
                    print()
                print(list(json['actions']['active'][0].keys()))
                print(list(json['actions']['passive'][0].keys()))
                break
    finally:
        stop_processor()


def print_skill(n):
    start_processor()
    try:
        while True:
            json = processor.get()
            json = json['b']['o']
            if json.get('cmd') == 'sAct':
                for i, skill in enumerate(json['actions']['active']):
                    if i == n - 1:
                        for key, value in skill.items():
                            print(f'{key}: {value}')
                break
    finally:
        stop_processor()


def print_ct():
    start_processor()
    try:
        n = 0
        while n < 5:
            json = processor.get()
            json = json['b']['o']
            if json.get('cmd') == 'ct':
                n += 1
                for key, value in json.items():
                    print(f'{key} - {value}')
                print()
    finally:
        stop_processor()


def print_drops():
    start_processor()
    num = 0
    for i in range(300):
        json = processor.get(0.1)
        if json:
            try:
                extracted_json = json['b']['o']
                if extracted_json['cmd'] in ['dropItem', 'addItems', 'getDrop']:
                    num += 1
                    print(f'{num} - {extracted_json}')
            except KeyError:
                pass
    processor.stop()
    processor.join()
    game_sniffer.stop()


def get_inventory():
    start_processor()
    try:
        while True:
            json = processor.get()
            json = json['b']['o']
            if json.get('cmd') == 'loadInventoryBig':
                for item in json['items']:
                    print(item['sName'], item['iRng'], item.get('EnhRng'))
                break
    finally:
        stop_processor()


if __name__ == '__main__':
    print('Test started.\n')
    print_live()
    print('\nTest finished.')
