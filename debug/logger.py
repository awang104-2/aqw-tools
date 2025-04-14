import logging
import os


path = os.path.dirname(__file__)


class Logger:

    def __init__(self, filename, name=None):
        if not name:
            name = __name__
        self.filepath = os.path.join(path, 'logs', filename)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(self.filepath, mode='a')  # mode='w' to overwrite
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(file_handler)

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

