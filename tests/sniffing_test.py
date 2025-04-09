from game.game_sniffer import GameSniffer
from network.sniffing import Sniffer
from pynput.keyboard import Listener, Key
from game.aqw_backend import AQW_SERVERS
from network.layers import Raw


def on_release(key, sniffer):
    if key == Key.esc:
        try:
            sniffer.stop()
        except RuntimeError:
            pass
        return False

def aqw_game_sniff_test():
    game_sniffer = GameSniffer(server='twig')
    game_sniffer.summary_on = True
    function = lambda key: on_release(key, game_sniffer)
    listener = Listener(on_release=function)
    game_sniffer.start()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    listener.run()
    print('Finished.')


def aqw_sniff_test():
    twig = AQW_SERVERS.get('twig')
    sniffer = Sniffer(f'tcp and (src host {twig} or dst host {twig})', layers=[Raw], summary_on=True)
    function = lambda key: on_release(key, sniffer)
    listener = Listener(on_release=function)
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    sniffer.start()
    listener.run()
    print('Finished.')


if __name__ == '__main__':
    aqw_sniff_test()
