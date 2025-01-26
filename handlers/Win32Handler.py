import win32process
import win32gui
from pywinauto import Application
from pywinauto.findwindows import find_elements


def get_window_names():
    win_names = []

    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            win_names.append([hwnd, win32gui.GetWindowText(hwnd)])
    win32gui.EnumWindows(winEnumHandler, None)
    return win_names


def list_window_names():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(hwnd, "'" + win32gui.GetWindowText(hwnd) + "'")
    win32gui.EnumWindows(winEnumHandler, None)


def list_child_windows_by_hwnd(parent_hwnd: int):
    win32gui.EnumChildWindows(parent_hwnd, enum_child_windows, None)


def list_child_windows_by_name(parent_name: str):
    parent_hwnd = win32gui.FindWindow(None, parent_name)
    win32gui.EnumChildWindows(parent_hwnd, enum_child_windows, None)


def enum_child_windows(hwnd, lparam):
    # Get the window text
    text = win32gui.GetWindowText(hwnd)

    # Print the window handle and text
    print(hwnd, "'" + text + "'")

    # Return True to continue enumerating
    return True


def get_window_pid(hwnd):
    thread_id, pid = win32process.GetWindowThreadProcessId(hwnd)
    return pid


def get_window_dimensions(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    return left, top, width, height


def get_client_hwnd(name='GameLauncher on Artix Entertainment v.212'):
    app = Application(backend='win32').connect(title=name, timeout=3)
    client = app['Chrome_WidgetWin_1']
    return client.handle


def list_windows():
    elements = find_elements()
    for element in elements:
        print(f"Title: {element.name}, Process ID: {element.process_id}, Class Name: {element.class_name}")


