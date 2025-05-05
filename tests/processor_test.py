import multiprocessing
from network.processing import Processor
from game.updater import GameSniffer
from tkinter import Tk, Label, Button
import datetime
import time


_last_after_id = None


def increment_clock(starting_time, label):
    global _last_after_id
    current_time = time.time() - starting_time
    current_time = datetime.timedelta(seconds=int(current_time))
    label.config(text=current_time)
    _last_after_id = label.after(100, increment_clock, starting_time, label)


def start(sniffer, processor, button, label):
    global _last_after_id
    sniffer.start()
    processor.start()
    button.config(text='STOP', command=lambda: stop(sniffer, processor, button, label))
    start_time = time.time()
    _last_after_id = label.after(100, increment_clock, start_time, label)


def stop(sniffer, processor, button, label):
    label.after_cancel(_last_after_id)
    print('Stopping sniffer.')
    sniffer.stop()
    print('Sniffer stopped.')
    # print(sniffer.packets)
    print('Stopping processor.')
    processor.stop()
    print('Processor stopped.')
    print(multiprocessing.active_children())
    button.config(text='START', command=lambda: start(sniffer, processor, button, label))


def create_clock(sniffer, processor):
    window = Tk()
    window.attributes('-topmost', True)
    window.geometry('300x150+0+0')
    label = Label(window, text='Clock', font=('Helvetica', 50))
    button = Button(window, text='START', font=('Arial', 20))
    button.config(command=lambda: start(sniffer, processor, button, label))
    label.pack()
    button.pack()
    window.mainloop()


def create_sniffer_processor(server):
    sniffer = GameSniffer(server)
    processor = Processor(sniffer)
    return sniffer, processor


if __name__ == '__main__':
    args = create_sniffer_processor('any')
    create_clock(*args)
