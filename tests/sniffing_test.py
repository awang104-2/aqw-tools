from game.game_sniffer import GameSniffer
from pynput.keyboard import Listener, Key


def on_release(key, sniffer):
    if key == Key.esc:
        try:
            sniffer.stop()
        except RuntimeError:
            pass
        return False

def aqw_sniff_test():
    game_sniffer = GameSniffer(server='twig')
    game_sniffer.summary_on = True
    function = lambda key: on_release(key, game_sniffer)
    listener = Listener(on_release=function)
    game_sniffer.start()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    listener.run()
    print('Finished.')


if __name__ == '__main__':
    aqw_sniff_test()
