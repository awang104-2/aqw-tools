from bot.autoclicker import AutoClicker
from pynput.keyboard import Listener, Key
from threading import Thread, Event
from time import sleep, time


def on_release(key, flag):
    if key == Key.esc:
        flag.clear()
        return False


def autoclick_thread(autoclicker, keys, t, flag):
    def autoclick_loop():
        flag.set()
        while flag.is_set():
            for key in keys:
                autoclicker.press(key)
                sleep(t)
    return Thread(target=autoclick_loop)


def main():
    autoclicker = AutoClicker()
    flag = Event()
    autoclicker_thread = autoclick_thread(autoclicker=autoclicker, keys=('2', '3', '4' ,'5'), t=0.1, flag=flag)
    listener = Listener(on_release=lambda key: on_release(key, flag))
    autoclicker_thread.start()
    listener.run()


def sleep_print(t):
    start_time = time()
    sleep(t)
    end_time = time()
    print(end_time - start_time)


if __name__ == '__main__':
    autoclicker = AutoClicker()
    sleep(1)
    for __ in range(50):
        autoclicker.press('5')
        sleep_print(0.75)
        autoclicker.press('3')
        sleep_print(0.75)
        autoclicker.press('2')
        sleep_print(0.75)
        autoclicker.press('4')
        sleep_print(0.75)
        autoclicker.press('2')
        sleep_print(0.75)
        autoclicker.press('4')
        sleep_print(0.75)
        autoclicker.press('2')
        sleep_print(0.75)
        autoclicker.press('4')
        sleep_print(0.75)
        autoclicker.press('2')
        sleep_print(0.75)
        autoclicker.press('4')
        sleep_print(0.75)
