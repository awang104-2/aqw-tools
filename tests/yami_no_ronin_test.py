from bot.autoclicker import AutoClicker
from game.updater import GameSniffer
from network.processing import Processor, print_all_processes
from threading import Thread
from time import sleep, time


def create_sniffer_and_processor(server, connect=False):
    game_sniffer = GameSniffer(server)
    processor = Processor(game_sniffer)
    if connect:
        game_sniffer.start()
        processor.start()
    return game_sniffer, processor


def create_autoclicker(connect=False):
    autoclicker = AutoClicker()
    if connect:
        autoclicker.connect()
    return autoclicker


def combat_thread(autoclicker, start=False):
    def combat(combo=2):
        match combo:
            case 1:
                combo = [(3, 0.75), (2, 1.5), (2, 0.75), (5, 0.75), (2, 1.5), (2, 0.75), (5, 0.75), (2, 1.5), (2, 0.75), (5, 0.75), (2, 1.5), (2, 0.75), (5, 0.75)]
            case 2:
                combo = [(3, 0.75), (2, 1.5), (5, 0.75), (2, 1.5), (2, 0.75), (5, 0.75), (2, 1.5), (2, 0.75), (5, 0.75), (2, 1.5), (2, 0.75), (5, 0.75)]
        try:
            for _ in range(10):
                start_time = 0
                for i in combo:
                    n = i[0]
                    autoclicker.press(f'{i[0]}')
                    if n == 3:
                        start_time = time()
                    sleep(i[1])
                    sleep(0.02)
                end_time = time()
                if end_time - start_time <= 11:
                    sleep(11 - (end_time - start_time))
        finally:
            pass
            # autoclicker.disconnect()
    thread = Thread(target=combat)
    if start:
        thread.start()
    return thread


def ynr():
    autoclicker = create_autoclicker(True)
    game_sniffer, processor = create_sniffer_and_processor('twig', True)
    combat_thread(autoclicker, True)
    print_all_processes()
    try:
        prev_json = None
        for i in range(300):
            json = processor.get()['b']['o']
            if json == prev_json:
                continue
            if json.get('cmd') == 'stu':
                prev_json = json
                dodge = json['sta'].get('$tdo')
                if dodge and dodge < 0.85:
                    print(dodge)
    finally:
        processor.stop()
        game_sniffer.stop()


if __name__ == '__main__':
    sleep(2)
    ynr()