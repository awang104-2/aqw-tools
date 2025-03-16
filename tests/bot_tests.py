from bot.player import Player
from pynput.keyboard import Listener, Key


def run_listener(player):

    def on_press(key):
        if key == Key.esc:
            player.stop(print_logs=True)
            return False

    listener = Listener(on_press=on_press)
    listener.start()


def combat_loop(player, flag):
    while flag.is_set():
        player.fight()


if __name__ == '__main__':
    print('\nTest Finished.')
