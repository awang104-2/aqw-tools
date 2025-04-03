from bot.autoclicker import AutoClicker
from pynput.keyboard import Listener, Key
from threading import Thread, Event
from time import sleep


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


if __name__ == '__main__':
    main()
