from network.processing import Processor
from pynput.keyboard import Listener, Key
from network.sniffing import Sniffer
from game.game_sniffer import GameSniffer
from network.layers import Raw
from time import sleep
from game.aqw_backend import AQW_SERVERS


def on_release(key, sniffer, processor):
    if key == Key.esc:
        processor.stop()
        sniffer.stop()
        return False
    elif key == Key.ctrl_l:
        pass


def processor_with_game_sniffer():
    sniffer = GameSniffer(server='twig')
    listener = Listener(on_release=lambda key: on_release(key, sniffer, processor))
    processor = Processor(sniffer=sniffer)
    sniffer.start()
    processor.start()
    processor.print.set()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    listener.run()
    sleep(1)
    print('Finished.')


def get_and_print_packet_new(processor):
    packet = processor.get_packet()['b']['o']
    if packet.get('cmd') == 'addGoldExp' and packet.get('typ') == 'm':
        print(packet)


def raw_processor():
    twig_ip = AQW_SERVERS.get('twig')
    bpf_filter = f'tcp and (src host {twig_ip} or dst host {twig_ip})'
    sniffer = Sniffer(bpf_filter, [Raw], False)
    listener = Listener(on_release=lambda key: on_release(key, sniffer, processor))
    processor = Processor(sniffer=sniffer)
    processor.print.set()
    processor.get_and_print_packet = lambda: get_and_print_packet_new(processor)
    sniffer.start()
    processor.start()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    listener.run()
    processor.join()
    print('Finished.')


if __name__ == '__main__':
    raw_processor()