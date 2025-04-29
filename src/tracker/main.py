from gui import MainWindow
from debug.logger import get_file_names, get_unique_filename
from multiprocessing import active_children
from threading import Thread, Event


def main():
    flag = Event()
    flag.set()
    file_names = get_file_names()
    filename = 'log.txt'
    filename = get_unique_filename(filename, file_names)
    character = Character()
    updater = Updater(server='any', character=character, daemon=True, log=filename)
    main_window = MainWindow(updater, filename)
    main_window.run()
    print('finished running')
    updater.stop()
    updater.disconnect()


if __name__ == '__main__':
    main()

