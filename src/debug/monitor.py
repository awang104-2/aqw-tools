import psutil
import time
import os
import threading


def get_process(pid=None):
    if not pid:
        pid = os.getpid()
    return psutil.Process(pid)


def print_pids():
    print(psutil.pids())


def monitor_process(process, flag, log_file=os.path.join(os.path.dirname(__file__), 'logs', 'cpu_usage_log.txt')):
    """ Continuously logs CPU usage of each thread in the Python process. """
    with open(log_file, "w") as f:
        f.write("Timestamp, Thread ID, CPU Usage (%)\n")  # CSV Header
        t = 1
        while True:
            log_entries = []

            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            cpu_usage = process.cpu_percent(interval=t)
            log_entries.append(f"{timestamp}, {process.pid}, {cpu_usage}")

            f.write("\n".join(log_entries) + "\n")
            f.flush()  # Ensure data is written to the file immediately
            time.sleep(0.01)  # Adjust sampling rate as needed

            if flag.is_set():
                break


def monitor_parallel(flag):
    process = get_process()
    t = threading.Thread(target=monitor_process, args=[process, flag], daemon=True)
    t.name = 'monitor thread'
    t.start()