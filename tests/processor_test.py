from game.game_sniffer import GameSniffer
from network.processing import Processor


game_sniffer = GameSniffer(server='twig')
processor = Processor(game_sniffer)
undistorted = []
distorted = []


def main():
    game_sniffer.start()
    processor.start()
    for i in range(300):
        json = processor.get(0.1)
        if json:
            try:
                extracted_json = json['b']['o']
                undistorted.append(extracted_json)
                print(extracted_json)
            except KeyError:
                distorted.append(json)
    processor.stop()
    processor.join()
    game_sniffer.stop()
    print('\n\nUndistorted:')
    for json in undistorted:
        print(json)
    print('\nDistorted:')
    for json in distorted:
        print(json)


if __name__ == '__main__':
    main()
