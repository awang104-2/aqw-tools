from bot.player import AutoPlayer
from pynput.keyboard import Key, Listener
from debug.monitor import monitor_parallel
import threading


flag = threading.Event()


def on_press(key, player):
    if key == Key.esc:
        flag.set()
        player.stop()
        print(f'\nDrops: {player.get_drops()}')
        return False


def run_listener(player):
    listener = Listener(on_press=lambda key: on_press(key, player))
    listener.start()


if __name__ == '__main__':
    resolution = input('Resolution > ')
    quest = input('Quest > ').split(',')
    server = input('Server > ')
    bot = AutoPlayer(resolution, quest, server)
    run_listener(bot)
    monitor_parallel(flag)
    bot.run()
    flag.set()

