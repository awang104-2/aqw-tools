from pywinauto import Application
import time


class AutoClicker:

    def __init__(self):
        app = Application(backend='win32').connect(title='GameLauncher on Artix Entertainment v.212', timeout=3)
        self.client = app['Chrome_WidgetWin_1']
        self.client.maximize()

    def click(self, coordinates):
        self.client.click(coords=coordinates)

    def press(self, key):
        self.client.send_keystrokes(key)

    def get_hwnd(self):
        return self.client.handle

    def type(self, string):
        self.client.send_keystrokes(string)
        self.wait(0.5)
        self.client.send_keystrokes('{ENTER}')

    def wait(self, t):
        time.sleep(t)

    def quit_client(self):
        self.client.close()

    def clear(self):
        """
        Releases all commonly stuck keys to reset the keyboard state.
        """

        # Release all keys
        for char in "l12345":
            self.client.send_keystrokes(char)

        print("All keys released.")


if __name__ == '__main__':
    import time
    import numpy as np
    from pynput.keyboard import Listener, Key

    def on_release(key):
        global running
        if key == Key.esc:
            running = False
            return False


    running = True
    autoclicker = AutoClicker()
    listener = Listener(on_release=on_release)
    listener.start()
    while running:
        for i in ['1', '2', '3', '4', '5']:
            autoclicker.press(i)
            delay = 0.20 + np.random.rand() * 0.1
            print(delay)
            time.sleep(delay)
    listener.join()
    autoclicker.clear()
    exit(1)

