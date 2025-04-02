from network.processing import Processor
from pynput.keyboard import Listener, Key
from network.sniffing import Sniffer
from network.layers import Raw


def on_release(key, sniffer, processor):
    if key == Key.esc:
        processor.stop()
        sniffer.stop()
        return False


def main():
    bpf_filter = 'tcp and src host 172.65.235.85'
    sniffer = Sniffer(bpf_filter=bpf_filter, layers=[Raw])
    listener = Listener(on_release=lambda key: on_release(key, sniffer, processor))
    processor = Processor(sniffer=sniffer)
    sniffer.start()
    processor.start()
    print('Press \'esc\' to exit.')
    print('Sniffing...')
    listener.run()
    print('Finished.')


if __name__ == '__main__':
    main()
