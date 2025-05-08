from pywinauto import Application, ElementNotFoundError
from threading import Lock
import time


class AutoClicker:

    def __init__(self):
        self.client = Application(backend='win32').connect(title='GameLauncher on Artix Entertainment v.212', timeout=5)
        self.ctrl = self.client.window(found_index=0)
        self._mouse_lock = Lock()
        self._keyboard_lock = Lock()

    def click(self, coordinates):
        with self._mouse_lock:
            self.ctrl.click(coords=coordinates)

    def press(self, key):
        with self._keyboard_lock:
            self.ctrl.send_keystrokes(key)

    def get_hwnd(self):
        return self.ctrl.handle

    def type(self, string):
        with self._keyboard_lock:
            for char in string:
                self.ctrl.send_keystrokes(char)
                self.wait(0.1)
            self.ctrl.send_keystrokes('{ENTER}')

    def wait(self, t):
        time.sleep(t)






