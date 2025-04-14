from pywinauto import Application
from threading import Lock
import time


class AutoClicker:

    def __init__(self):
        self.client = None
        self.ctrl = None
        self._mouse_lock = Lock()
        self._keyboard_lock = Lock()

    def connect(self):
        self.client = Application(backend='win32').connect(title='GameLauncher on Artix Entertainment v.212', timeout=5)
        self.ctrl = self.client.window(found_index=0)

    def disconnect(self):
        self._clear()
        self.client = None
        self.ctrl = None

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

    def _clear(self):
        """
        Releases all commonly stuck keys to reset the keyboard state.
        """
        keys_to_release = [
            "{VK_SHIFT up}",
            "{VK_CONTROL up}",
            "{VK_MENU up}",  # Alt key
            "{VK_LWIN up}",  # Windows key
            "{VK_TAB up}",
            "{VK_CAPITAL up}",  # Caps Lock
            "{VK_NUMLOCK up}",  # Num Lock
            "{VK_SCROLL up}",  # Scroll Lock
        ]

        # Add alphanumeric keys
        for char in "abcdefghijklmnopqrstuvwxyz0123456789":
            keys_to_release.append(f"{{{char} up}}")

        # Release all keys
        with self._keyboard_lock:
            for key in keys_to_release:
                self.ctrl.send_keystrokes(key)

        print("All keys released.")

    def clear(self):
        """
        Releases all commonly stuck keys to reset the keyboard state.
        """
        self._clear()

    def exit(self):
        self.disconnect()





