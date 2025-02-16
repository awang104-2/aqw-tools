from bot.player import AutoPlayer
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


def bot_test():
    resolution = input('Resolution > ')
    quest = input('Quest > ')
    server = input('Server > ')
    test_player = AutoPlayer(resolution=resolution, quest=quest, server=server)
    run_listener(test_player)
    test_player.run()

if __name__ == '__main__':
    bot_test()
    print('\nTest Finished.')
