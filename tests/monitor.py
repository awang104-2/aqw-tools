import time
import psutil
import os


def monitor(interval, count):
    string = ''
    process = psutil.Process(os.getpid())
    for i in range(count):
        start_time = time.time()
        cpu = process.cpu_percent(interval=interval)
        mem = process.memory_info().rss / 1024 ** 2  # in MB
        end_time = time.time()
        string += f"{i + 1} - CPU: {cpu}% | Memory: {mem:.2f} MB | {round(end_time - start_time, 2)}s\n"
    return string


def random_function(label):
    if label.cget('text') == 'hello':
        label.config(text='goodbye')
    else:
        label.config(text='hello')
    label.after(1000, random_function, label)

if __name__ == '__main__':
    import tkinter
    window = tkinter.Tk()
    label = tkinter.Label(window)
    label.pack()
    window.after(100, random_function, label)
    window.mainloop()