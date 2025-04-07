from bot.player import Player
from pynput.keyboard import Listener, Key
from threading import Event


def on_release(released_key, flag):
    if released_key == Key.esc:
        flag.clear()
        return flag


flag = Event()
flag.set()
keys = ('4', '5', '2', '3')
player = Player('2256x1504', 'artix', 'lr')
listener = Listener(on_release=lambda released_key: on_release(released_key, flag))


if __name__ == '__main__':
    listener.start()
    player.attack('4')
    while flag.is_set():
        key = player.wait(keys)
        player.attack(key)
