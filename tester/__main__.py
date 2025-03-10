from tester.tests import string_tests
from tester.tests import sniffer_tests
from tester.tests import autoclicker_tests
from tester.tests import bot_tests
import pynput
import time


def pynput_test():
    mouse = pynput.mouse.Controller()
    while True:
        coordinates = input('Input or \'exit\' > ')
        if coordinates.lower() == 'exit':
            break
        else:
            time.sleep(1)
            x, y = coordinates.split(',')
            mouse.position = (int(x), int(y))
            time.sleep(0.5)


def prompt():
    print('1 - Compare resolution of two images')
    print('2 - Sniff AQW packets')
    print('3 - Log drop packets')
    print('4 - Click test')
    print('5 - Sniff all packets')
    print('6 - Bot Test')
    print('7 - Pynput Test')
    choice = input('Pick a test or type \'exit\' to quit > ')
    return int(choice)


def run_test(choice):
    match choice:
        case 'exit':
            return
        case 1:
            string_tests.string_split_test()
        case 2:
            exclusions = input('Exclude > ').split(',')
            if exclusions == '':
                exclusions = None
            sniffer_tests.sniff_aqw_test(exclude=exclusions)
        case 3:
            sniffer_tests.drop_test()
        case 4:
            autoclicker_tests.click_test()
        case 5:
            server = input('Server > ')
            bpf_filter = sniffer_tests.get_bpf_filter('tcp and src host', server)
            sniffer_tests.sniff_test(bpf_filter)
        case 6:
            bot_tests.bot_test_2()
        case 7:
            pynput_test()


if __name__ == '__main__':
    test = prompt()
    run_test(test)



