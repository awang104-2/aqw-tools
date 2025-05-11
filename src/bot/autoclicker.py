from pywinauto import Application, mouse
from pywinauto.controls.hwndwrapper import HwndWrapper
from pywinauto.findwindows import find_windows
from threading import Lock
import time


client_title = 'Artix Game Launcher'


def list_all_windows():
    windows = find_windows()
    for handle in windows:
        window = HwndWrapper(handle)
        print(f"Handle: {handle} | PID: {window.process_id()} | Title: \'{window.window_text()}\' | Class: {window.class_name()}")


def get_windows(title):
    windows = []
    for handle in find_windows():
        window = HwndWrapper(handle)
        if window.window_text() == title:
            windows.append(window)
    return windows


def launch_game():
    pass


class AutoClicker:

    handles = []

    @staticmethod
    def reset_handles():
        AutoClicker.handles = []

    def __init__(self):
        windows = get_windows(client_title)
        self.client = None
        self.ctrl = None
        for window in windows:
            if window.handle not in AutoClicker.handles:
                self.client = Application(backend='win32').connect(title=client_title, handle=window.handle)
                self.ctrl = self.client.window(title=client_title, handle=window.handle)
                AutoClicker.handles.append(window.handle)
                break
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



