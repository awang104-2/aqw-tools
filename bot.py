from autoclicker import AutoClicker
from threading import Thread
import time
from actions import Quest, Move


class Bot:

    def __init__(self, routine=['2', '3', '4', '5'], running=False, delay=1):
        self.clicker = AutoClicker()
        self.running = running
        self.routine = routine
        self.delay = delay
        self.threads = []
        self.timer = 0

    def start(self):
        self.timer = 0
        self.running = True
        self.threads.append(Thread(target=self.thread))
        for thread in self.threads:
            thread.start()

    def stop(self):
        self.running = False
        for thread in self.threads:
            thread.join()
        self.threads = []

    def thread(self):
        routine = self.routine.copy()
        quest = Quest(self.clicker, num_quests=1)
        while self.running:
            if self.timer == 300:
                quest.complete_quest()
                self.timer = 0
            else:
                self.clicker.press(routine[0])
                routine = routine[1:] + [routine[0]]
                time.sleep(self.delay)

    def change_routine(self, routine=[], delay=None):
        if routine:
            self.routine = routine
        if delay:
            self.delay = delay


