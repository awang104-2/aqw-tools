from game.game_sniffer import GameSniffer
from network.processing import Processor
from bot.autoclicker import AutoClicker
from pynput.keyboard import Listener, Key
import time


Processor._original_function = Processor._print_jsons
start_time = None


def loop():
    autoclicker = AutoClicker()
    for i in range(100):
        autoclicker.press('4')
        time.sleep(0.75)
        autoclicker.press('3')
        time.sleep(5)


def monkey_patched_function(self, jsons):
    global start_time
    diff = None
    if not start_time and any(jsons):
        start_time = time.time()
    if any(jsons):
        diff = time.time() - start_time
    return Processor._original_function(self, jsons, f'{diff}')


def new_listener(*args):
    def on_release(key):
        if key == Key.esc:
            for arg in args:
                arg.stop()
            return False
    return Listener(on_release=on_release)


if __name__ == '__main__':
    Processor._print_jsons = monkey_patched_function
    sniffer = GameSniffer('twig')
    processor = Processor(sniffer)
    processor.print.set()
    listener = new_listener(sniffer, processor)
    sniffer.start()
    processor.start()
    listener.start()
    print('Sniffing...')
    loop()


