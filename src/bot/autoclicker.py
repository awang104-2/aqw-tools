from pywinauto import Application, mouse
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import find_windows, ElementNotFoundError
from threading import Lock
import time


titles = ['GameLauncher on Artix Entertainment v.212', 'Artix Game Launcher', 'GameLauncher on Artix Entertainment v.220']


def list_all_windows():
    windows = find_windows()
    for handle in windows:
        window = HwndWrapper(handle)
        print(f"Title: \'{window.window_text()}\' | Class: {window.class_name()}")


class AutoClicker:

    found_index = 0

    def __init__(self):
        self.client = None
        for title in titles:
            try:
                self.client = Application(backend='win32').connect(title=title)
                break
            except ElementNotFoundError:
                pass
        if not self.client:
            raise ElementNotFoundError(f'{titles}')
        self.ctrl = self.client.window()
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


import win32api, win32con, win32gui


def silent_click(hwnd, x=0, y=0):
    lparam = win32api.MAKELONG(x, y)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
    win32gui.SendMessage(hwnd, win32con.WM_LBUTTONUP, 0, lparam)


def silent_scroll(hwnd, client_x=0, client_y=0, delta=120):
    """
    Sends a WM_MOUSEWHEEL message to hwnd at (client_x, client_y) without moving the cursor.

    :param hwnd: Window handle
    :param client_x: x coord inside window (client area)
    :param client_y: y coord inside window (client area)
    :param delta: 120 for scroll up, -120 for scroll down
    """
    # Convert client coords to screen coords
    point = win32gui.ClientToScreen(hwnd, (client_x, client_y))
    screen_x, screen_y = point

    # Pack coords into lParam
    lparam = win32api.MAKELONG(screen_x, screen_y)

    # wParam is high word = delta (scroll amount)
    wparam = win32api.MAKELONG(0, delta)

    # Send the scroll message
    win32gui.SendMessage(hwnd, win32con.WM_MOUSEWHEEL, wparam, lparam)



def silent_scroll_no_coords(hwnd, delta=120):
    # Positive delta = scroll up, negative = scroll down
    win32gui.SendMessage(hwnd, win32con.WM_MOUSEWHEEL, win32api.MAKELONG(0, delta), 0)


if __name__ == '__main__':
    autoclicker = AutoClicker()
    hwnd = autoclicker.ctrl.handle
    print(hwnd, type(hwnd))
    time.sleep(1)
    silent_click(hwnd, x=2000, y=700)
    silent_scroll(hwnd, client_x=2000, client_y=700, delta=-120)  # scroll down





