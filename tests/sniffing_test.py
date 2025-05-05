from tests.monitor import monitor
from network.sniffing import Sniffer
import time
import random


def test_ram_cpu(sniffer, interval, logs):
    sniffer.reset()
    print('Testing RAM and CPU usage.')
    print('Test started.')
    start_time = time.time()
    sniffer.start()
    result = monitor(interval, logs)
    sniffer.stop()
    end_time = time.time()
    print('Test ended.')
    print(f'Test Duration: {end_time - start_time}s')
    print(f'Results:\n{result}')


def test_reset(sniffer):
    sniffer.reset()
    print('Testing reset method.')
    print('Test started.')
    start_time = time.time()
    for i in range(3):
        try:
            print(f'Trial {i + 1} started.')
            sniffer.start()
            time.sleep(3)
            sniffer.stop()
            sniffer.reset()
            print(f'Trial {i + 1} completed.')
        except Exception as e:
            print(f'Trial {i + 1} failed: {e}')
    end_time = time.time()
    print('Test ended.')
    print(f'Test Duration: {end_time - start_time}s\n')


def test_errors(sniffer):
    sniffer.reset()
    print('Testing for errors.')
    print('Test started.')
    try:
        sniffer.start()
        sniffer.start()
    except Exception as e:
        print(f'Error Detected: {e}')
    try:
        sniffer.reset()
    except Exception as e:
        print(f'Error Detected: {e}')
    try:
        sniffer.stop()
        sniffer.stop()
    except Exception as e:
        print(f'Error Detected: {e}')
    print('Test ended.')


if __name__ == '__main__':
    sniffer = Sniffer('tcp')
    test_ram_cpu(sniffer, 0.1, 5)
    test_reset(sniffer)
    test_errors(sniffer)
