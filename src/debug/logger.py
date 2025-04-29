import itertools
import logging
import os


package = os.path.dirname(__file__)
project_root = os.path.dirname(os.path.dirname(package))
logs_path = os.path.join(project_root, 'logs')


def get_file_names():
    file_names = [f for f in os.listdir(logs_path) if os.path.isfile(os.path.join(logs_path, f)) and f.endswith('.txt')]
    return file_names


def get_unique_filename(filename, file_names):
    count = itertools.count(1, 1)
    while filename in file_names:
        new_filename = filename[:-4] + f'-{next(count)}' + '.txt'
        if not new_filename in file_names:
            filename = new_filename
    return filename


class Logger:

    def __init__(self, filename, name=None):
        if not name:
            name = __name__
        self.filepath = os.path.join(logs_path, filename)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.file_handler = logging.FileHandler(self.filepath, mode='a')  # mode='w' to overwrite
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        self.file_handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(self.file_handler)

    def close(self):
        self.logger.removeHandler(self.file_handler)
        self.file_handler.close()

    def clear(self):
        with open(self.filepath, 'w'):
            pass

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)

    def critical(self, msg: str):
        self.logger.critical(msg)



