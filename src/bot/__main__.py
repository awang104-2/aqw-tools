from bot.player import AutoPlayer
from pynput.keyboard import Key, Listener
from debug.monitor import *
import threading
import time


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


def print_inventory(player):
    while player.is_running():
        player.print_inventory()
        time.sleep(1)


def print_inventory_thread(player):
    thread = threading.Thread(target=print_inventory, args=[player])
    thread.start()


if __name__ == '__main__':
    while True:
        custom_settings = input('Yes or No or "exit" > ').lower()
        match custom_settings:
            case 'yes':
                resolution = input('Resolution > ')
                quest = input('Quest > ').split(',')
                server = input('Server > ')
                haste = float(input('Haste > '))
                cls = input('Class > ')
                bot = AutoPlayer(resolution, quest, server, haste, cls)
                run_listener(bot)
                monitor_parallel(flag)
                print_inventory_thread(bot)
                bot.run()
                flag.set()
                break
            case 'no':
                resolution = '2256x1504'
                quest = ['test']
                server = 'twig'
                bot = AutoPlayer(resolution, quest, server)
                run_listener(bot)
                monitor_parallel(flag)
                print_inventory_thread(bot)
                bot.run()
                flag.set()
                break
            case 'exit':
                break



