from threads.custom_threading import *
from time import sleep
from itertools import count
from pynput.keyboard import Listener, Key


class CustomThreadTester:

    def __init__(self):
        self.count = count()
        self.custom_thread = CustomThread(target=self.increment, loop=True)
        self.listener = Listener(on_release=self.on_release)

    def on_release(self, key):
        if key == Key.esc:
            if self.custom_thread.is_running():
                self.custom_thread.stop()
                print('Ready to start.')
            else:
                self.start()

    def increment(self):
        print(f'Step - {next(self.count)}')
        sleep(0.1)

    def start(self):
        self.custom_thread.start()
        self.listener.run()


if __name__ == '__main__':
    custom_thread_tester = CustomThreadTester()
    custom_thread_tester.start()