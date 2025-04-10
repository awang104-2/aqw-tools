from bot.player import Player
from game.character import Character
from pynput.keyboard import Listener, Key
from threading import Event
from time import sleep


flag = Event()
flag.set()
keys = ('4', '5', '2', '3')
player = Player(resolution='2256x1504', server='twig')
listener = Listener(on_release=lambda released_key: on_release(released_key, player, flag))


def on_release(released_key, player, flag):
    if released_key == Key.esc:
        flag.clear()
        return flag
    elif released_key == Key.ctrl_l or released_key == Key.ctrl_r:
        player.print()
        print('\n')


def player_test():
    listener.start()
    player.connect()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    while flag.is_set():
        sleep(0.1)
    print(player.interpreter.missed_packets)


def character_test():
    character = Character()
    character.reinitialize(class_name='lr', haste=0.5)
    character.reinitialize(location='battleon-1')
    print(character)


if __name__ == '__main__':
    # character_test()
    player_test()

