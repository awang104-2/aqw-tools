from gui import MainWindow
from debug.logging import get_file_names, get_unique_filename
from multiprocessing import active_children
from threading import Thread, Event


def main():
    flag = Event()
    flag.set()
    file_names = get_file_names()
    filename = 'log.txt'
    filename = get_unique_filename(filename, file_names)
    main_window = MainWindow(filename)
    main_window.run()
    print('finished running')
    updater.stop()
    updater.disconnect()


if __name__ == '__main__':
    main()

