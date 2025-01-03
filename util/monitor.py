from handlers.DataHandler import write_to_csv
import psutil
import time
import threading
import os
import numpy as np


def check(pid=None, dt=1):
    if pid:
        process = psutil.Process(pid)
        cpu_percent = process.cpu_percent(dt)
    else:
        cpu_percent = psutil.cpu_percent(dt)
    return cpu_percent


class UtilMonitor:

    def __init__(self):
        self.running = False
        self.cpu = []
        self.gpu = []
        self.active_threads = []

    def __call__(self, dt):
        if not self.running:
            target = lambda: self.loop_check(dt)
            t = threading.Thread(target=target)
            self.running = True
            t.start()
            self.active_threads.append(t)

    def stop(self):
        self.running = False
        for thread in self.active_threads:
            thread.join()
        write_to_csv(self.cpu, 'cpu_data.csv')

    def loop_check(self, dt):
        start_time = time.time()
        pid = os.getpid()
        while self.running:
            t = np.round(time.time() - start_time, decimals=3)
            cpu_percent = check(pid, dt)
            self.cpu.append({'time': t, 'cpu usage': cpu_percent})
            time.sleep(0.1)




