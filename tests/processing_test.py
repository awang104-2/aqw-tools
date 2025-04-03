from network.processing import Processor
from pynput.keyboard import Listener, Key
from network.sniffing import Sniffer
from network.layers import Raw
from time import sleep
from game.aqw_backend import AQW_SERVERS


def on_release(key, sniffer, processor):
    if key == Key.esc:
        processor.stop()
        sniffer.stop()
        return False


def main():
    bpf_filter = f'tcp and src host {AQW_SERVERS.get('twig')}'
    sniffer = Sniffer(bpf_filter=bpf_filter, layers=[Raw])
    listener = Listener(on_release=lambda key: on_release(key, sniffer, processor))
    processor = Processor(sniffer=sniffer)
    sniffer.start()
    processor.start()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    listener.run()
    sleep(1)
    print('Finished.')


if __name__ == '__main__':
    main()
