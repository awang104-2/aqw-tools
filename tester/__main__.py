from tester.tests import string_tests
from tester.tests import sniffer_tests
from tester.tests import autoclicker_tests



def prompt():
    print('1 - Compare resolution of two images')
    print('2 - Sniff packets')
    print('3 - Log item packets')
    print('4 - Click test')
    print('5 - Sniff all packets')
    choice = input('Pick a test or type \'exit\' to quit > ')
    return int(choice)


def run_test(choice):
    match choice:
        case 'exit':
            return
        case 1:
            string_tests.string_split_test()
        case 2:
            sniffer_tests.sniff_aqw_test(include=['dropItem', 'addItems', 'addGoldExp'])
        case 3:
            sniffer_tests.drop_test()
        case 4:
            autoclicker_tests.click_test()
        case 5:
            sniffer_tests.sniff_test(f'tcp and src 172.65.249.41')


if __name__ == '__main__':
    test = prompt()
    run_test(test)



