from multiprocessing import *
import time


class TestClass:

    def __init__(self):
        self.process = Process(target=self.method)
        self.queue = Queue()

    def method(self):
        for i in range(50):
            self.queue.put('hello')
            time.sleep(0.1)

    def start(self):
        self.process.start()

    def get(self):
        return self.queue.get()


if __name__ == '__main__':
    test_class = TestClass()
    test_class.start()
    time.sleep(0.2)
    test_class.get()



