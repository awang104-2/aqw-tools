import random
import time


if __name__ == '__main__':
    length = int(10 ** 7)
    m = random.randint(int(0.9 * length), length - 1)
    string = ''
    for i in range(length):
        if i == m:
            string += 'x'
        else:
            string += 'a'


    start_time = time.time()
    string.index('x')
    end_time = time.time()
    print(end_time - start_time)
    time.sleep(1)


    start_time = time.time()
    for char in string:
        if char == 'x':
            break
    end_time = time.time()
    print(end_time - start_time)
