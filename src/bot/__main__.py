from bot.player import AutoPlayer
from pynput.keyboard import Key, Listener
from debug.monitor import *
import threading


flag = threading.Event()


def on_press(key, player):
    if key == Key.esc:
        flag.set()
        player.stop()
        print(f'\nDrops: {player.get_drops()}')
        print(f'Active Thread Count: {threading.active_count()}')
        for i, x in enumerate(threading.enumerate()):
            print(f'{i + 1} - {x.name}')


def run_listener(player):
    listener = Listener(on_press=lambda key: on_press(key, player))
    listener.name = 'listener thread'
    listener.start()


if __name__ == '__main__':
    resolution = input('Resolution > ')
    quest = input('Quest > ').split(',')
    server = input('Server > ')
    haste = float(input('Haste > '))
    cls = input('Class > ')
    bot = AutoPlayer(resolution, quest, server, haste, cls)
    run_listener(bot)
    monitor_parallel(flag)
    bot.run()
    flag.set()

