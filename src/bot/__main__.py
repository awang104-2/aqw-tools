from bot.player import AutoPlayer
from pynput.keyboard import Key, Listener
from debug.monitor import *
import threading


flag = threading.Event()


def print_threads():
    print(f'\nActive Thread Count: {threading.active_count()}')
    for i, x in enumerate(threading.enumerate()):
        print(f'{i + 1} - {x.name}')


def on_press(key, player):
    if key == Key.esc:
        flag.set()
        player.stop()
        player.print_drops()
        print_threads()


def run_listener(player):
    listener = Listener(on_press=lambda key: on_press(key, player))
    listener.name = 'listener thread'
    listener.start()


if __name__ == '__main__':
    custom_settings = input('Yes or No > ').lower()
    match custom_settings:
        case 'yes':
            resolution = input('Resolution > ')
            quest = input('Quest > ').split(',')
            server = input('Server > ')
            haste = float(input('Haste > '))
            cls = input('Class > ')
            bot = AutoPlayer(resolution, quest, server, haste, cls)
        case 'no':
            resolution = '2256x1504'
            quest = ['test']
            server = 'twig'
            bot = AutoPlayer(resolution, quest, server)
    import time
    time.sleep(2)
    bot.turn_in_quests(3)
    # run_listener(bot)
    # monitor_parallel(flag)
    # bot.run()
   #  flag.set()

