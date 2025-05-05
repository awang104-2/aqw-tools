from gui import MainWindow
from debug.logging import get_file_names, get_unique_filename
from multiprocessing import active_children
from threading import Thread, Event


def main():
    children = active_children()
    for child in children:
        print(f'Terminating {child}.')
        child.terminate()
        child.join()


if __name__ == '__main__':
    main()

