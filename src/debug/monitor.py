import psutil
import time
import os
import threading


def monitor_threads(flag, log_file=os.path.join(os.path.dirname(__file__), 'logs', 'cpu_usage_log.txt')):
    """ Continuously logs CPU usage of each thread in the Python process. """
    pid = os.getpid()
    process = psutil.Process(pid)

    with open(log_file, "w") as f:
        f.write("Timestamp, Thread ID, CPU Usage (%)\n")  # CSV Header

        while True:
            log_entries = []
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            for thread in process.threads():
                thread_info = psutil.Process(thread.id)
                cpu_usage = thread_info.cpu_percent(interval=0.1)
                log_entries.append(f"{timestamp}, {thread.id}, {cpu_usage}")

            f.write("\n".join(log_entries) + "\n")
            f.flush()  # Ensure data is written to the file immediately
            time.sleep(0.5)  # Adjust sampling rate as needed

            if flag.is_set():
                break


def monitor_parallel(flag):
    t = threading.Thread(target=monitor_parallel, args=[flag], daemon=True)
    t.start()