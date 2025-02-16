from pywinauto import Application
import time


class AutoClicker:

    def __init__(self, title='GameLauncher on Artix Entertainment v.212'):
        self.client = Application(backend='win32').connect(title=title, timeout=5)
        self.ctrl = self.client.window(found_index=0)

    def click(self, coordinates):
        self.ctrl.click(coords=coordinates)

    def press(self, key):
        self.ctrl.send_keystrokes(key)

    def get_hwnd(self):
        return self.ctrl.handle

    def type(self, string):
        self.ctrl.send_keystrokes(string)
        self.wait(0.5)
        self.ctrl.send_keystrokes('{ENTER}')

    def wait(self, t):
        time.sleep(t)

    def clear(self):
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
        for key in keys_to_release:
            self.ctrl.send_keystrokes(key)

        print("All keys released.")




