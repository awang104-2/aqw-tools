from tkinter import *
from debug.logger import Logger
from threading import Thread, Event, Lock
from bot.autoclicker import AutoClicker
from game.updater import Updater
from game.character import Character


BASE_DPI = 96


def get_dpi_scaling(root):
    dpi = root.winfo_fpixels('1i')
    return round(dpi/BASE_DPI, 3)


class MainWindow:

    def __init__(self):
        self.updater = Updater()
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.frame = Frame(self.root)
        self.frame.pack(side='bottom', pady=20)
        self.scaling_factor = get_dpi_scaling(self.root)
        self.root.geometry(f'{int(250 * self.scaling_factor)}x{int(200 * self.scaling_factor)}-0+0')
        self.root.attributes('-topmost', True)
        self.name = Label(self.root, font=("Arial", 12, "bold"))
        self.name.pack()
        self.info = Label(self.root, font=("Arial", 8, "normal"))
        self.info.pack()
        self.status = Label(self.root, font=("Arial", 8, "normal"))
        self.status.pack()
        self.connect_button = Button(self.frame, text='START', command=self.start_updating)
        self.connect_button.pack(side='left')
        self.reset_button = Button(self.frame, text='RESET', command=self.reset)
        self.reset_button.pack(side='left')
        self.save_button = Button(self.frame, text='SAVE', command=self.save)
        self.save_button.pack(side='left')
        self.fight_button = Button(self.frame, text='FIGHT', command=self.fight)
        self.fight_button.pack(side='left')
        self._lock = Lock()
        self.logger = Logger(log, 'main window')
        self.flag = Event()
        self.autoclicker = AutoClicker()
        self._last_after = None

    def fight(self):
        if not self.flag.is_set():
            Thread(target=self.combat_loop, daemon=True).start()
            self.fight_button.config(text='STOP TEST')
        else:
            self.flag.clear()
            self.fight_button.config(text='RUN TEST')

    def combat_loop(self):
        character = self.updater.character
        self.flag.set()
        self.autoclicker.connect()
        while True:
            for i in ['1', '2', '3', '4', '5']:
                self.autoclicker.press(i)
                self.autoclicker.wait(0.1)
                if character.crit_data().get('total') >= 2000:
                    self.fight()
                if not self.flag.is_set():
                    self.autoclicker.disconnect()
                    return

    def _reset(self):
        print(f'called reset')
        print(f'acquiring lock')
        with self._lock:
            if not self.updater.connected('any'):
                self.updater = Updater()
            self.connect_button.config(state='normal')
        print(f'lock released')

    def reset(self):
        Thread(target=self._reset).start()

    def _start_updating(self):
        with self._lock:
            self.updater.connect()
            self.updater.start()

    def _stop_updating(self):
        with self._lock:
            self.updater.stop()
            self.updater.disconnect()

    def start_updating(self):
        Thread(target=self._start_updating).start()
        self.logger.info('Changing Start/Stop button to Start.')
        self.connect_button.config(text='STOP', command=self.stop_updating)
        self.logger.info('Disabling reset and save buttons.')
        self.reset_button.config(state='disabled')
        self.save_button.config(state='disabled')

    def stop_updating(self):
        Thread(target=self._stop_updating).start()
        self.logger.info('Changing Start/Stop button to Stop.')
        self.connect_button.config(state='disabled', text='START', command=self.start_updating)
        self.logger.info('Enabling reset and save buttons.')
        self.reset_button.config(state='normal')
        self.save_button.config(state='normal')

    def mainloop(self):
        self.root.mainloop()

    def after(self, time=100):
        character = self.updater.character
        name = character.get_class_name()
        self.name.config(text=name)
        info = character.get_skills_as_str() + '\n\n' + character.total_data_as_str()
        self.info.config(text=info)
        self._last_after = self.root.after(time, self.after, time)

    def run(self):
        self.logger.info('Running main window.')
        self.after()
        self.mainloop()

    def save(self):
        Thread(target=self.updater.character.save).start()

    def quit(self):
        # self.root.after_cancel(self._last_after)
        self.root.destroy()




