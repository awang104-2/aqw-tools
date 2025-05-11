import multiprocessing
import random


def make_queue(size):
    ret = multiprocessing.Queue()
    for i in range(size):
        ret.put(i)
    return ret


def make_pipe(size):
    """
    Function to check the maximum data a pipe can store. Try inputting a high value for arg size.
    """

    w, r, = multiprocessing.Pipe()
    for i in range(1, size):
        print(i)
        w.send(random.randint(int(10e6), int(10e10)))  # If the argument size is high enough, this will eventually deadlock and the process will hang
    return w, r


w, r = make_pipe(10000)
print('done')
# test_queue = make_queue(3575)
# print(test_queue.qsize())