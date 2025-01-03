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
            self.client.send_keystrokes(key)

        print("All keys released.")


