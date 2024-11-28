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


