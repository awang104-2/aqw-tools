from bot.player import AutoPlayer
from pynput.keyboard import Key, Listener


def on_press(key, player):
    if key == Key.esc:
        player.stop()
        print(f'\nDrops: {player.get_drops()}')
        return False


def run_listener(player):
    listener = Listener(on_press=lambda key: on_press(key, player))
    listener.start()


if __name__ == '__main__':
    resolution = input('Resolution > ')
    quest = input('Quest > ')
    server = input('Server > ')
    bot = AutoPlayer(resolution, quest, server)
    run_listener(bot)
    bot.run()
