from game.updater import GameSniffer
from time import sleep
from scapy.all import Raw


def main():
    game_sniffer = GameSniffer(server='twig')
    game_sniffer.start()
    sleep(10)
    game_sniffer.stop()
    while not game_sniffer.packets.empty():
        packet = game_sniffer.get()
        packet = packet[Raw].load
        print(packet)


if __name__ == '__main__':
    main()
