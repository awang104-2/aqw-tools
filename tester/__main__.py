import numpy as np
from tester.tests import image_tests, sniffer_tests


def prompt(options):
    while True:
        choice = input('Pick a test or type \'exit\' to quit > ')
        if choice.lower() == 'exit':
            return 'exit'
        try:
            choice = int(choice)
        except ValueError:
            print('Invalid input: only numbers allowed.')
            continue
        if choice not in options:
            print('Invalid option.')
        else:
            return choice


def run_test(choice):
    match choice:
        case 'exit':
            return
        case 1:
            image_tests.different_resolution_image_comparison()
        case 2:
            sniffer_tests.sniff_test(exclude=['ct'])
        case 3:
            sniffer_tests.supplies_quest_test()


if __name__ == '__main__':
    test = prompt(np.array(range(3)) + 1)
    run_test(test)

