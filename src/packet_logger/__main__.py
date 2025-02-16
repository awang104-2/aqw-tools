from threads import Event
from packet_logger.sniffer import AqwPacketLogger
from pynput.keyboard import Listener, Key
from time import sleep


if __name__ == '__main__':
    running = Event()
    server = input('Server > ').lower()
    sniffer = AqwPacketLogger(server=server)

    def on_release(key):
        if key == Key.esc and running.is_set():
            print('Stopping...')
            sniffer.stop()
            running.clear()
            return running.is_set()

    listener = Listener(on_release=on_release)
    running.set()
    sniffer.start()
    listener.start()

    while running.is_set():
        data = sniffer.parse_packets_to_data()
        for i, entry in enumerate(data):
            print(f'Entry {i}: {entry}')
        sleep(0.1)

    sniffer.stop()
    listener.join()
    print('Ended.')
