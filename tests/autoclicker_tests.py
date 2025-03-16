from bot.autoclicker import AutoClicker
from time import sleep


def click_test():
    autoclicker = AutoClicker()
    while True:
        coordinates = input('Type coordinates or type \'exit\' to quit > ' ).lower()
        if coordinates == 'exit':
            return
        coordinates.strip()
        coordinates.replace('(', '')
        coordinates.replace(')', '')
        x, y = coordinates.split(',')
        x, y = int(x), int(y)
        autoclicker.click((x, y))
        sleep(0.5)