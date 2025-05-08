from tkinter import *
from threading import Thread, Event, Lock
from bot.autoclicker import AutoClicker
from game.updater import Updater
from game.character import Character


BASE_DPI = 96


def get_dpi_scaling(root):
    dpi = root.winfo_fpixels('1i')
    return round(dpi/BASE_DPI, 3)


class MainWindow:

    width = 400
    height = 300
    x_offset = 0
    y_offset = 0

    def __init__(self):
        # Tkinter Window
        self.root = Tk()
        self.scaling_factor = get_dpi_scaling(self.root)
        self.width = int(self.width * self.scaling_factor)
        self.height = int(self.height * self.scaling_factor)
        self.x_offset = int(self.x_offset * self.scaling_factor)
        self.y_offset = int(self.y_offset * self.scaling_factor)
        self.root.geometry(f'{self.width}x{self.height}-{self.x_offset}+{self.y_offset}')
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        # Labels
        self.name = Label(self.root, font=("Arial", 16, "bold"))
        self.name.pack()
        self.info = Label(self.root, font=("Arial", 12, "normal"))
        self.info.pack()
        self.status = Label(self.root, font=("Arial", 12, "normal"))
        self.status.pack()

        # Buttons
        self.frame = Frame(self.root)
        self.frame.pack(side='bottom', pady=20)
        self.connect_button = Button(self.frame, text='START', command=self.start_updating)
        self.connect_button.pack(side='left')
        self.reset_button = Button(self.frame, text='RESET', command=self.reset)
        self.reset_button.pack(side='left')
        self.save_button = Button(self.frame, text='SAVE', command=self.save)
        self.save_button.pack(side='left')
        self.fight_button = Button(self.frame, text='FIGHT', command=self.fight)
        self.fight_button.pack(side='left')

        # Other
        self.updater = Updater(character=Character(), server='twig')
        self.autoclicker = AutoClicker()
        self.flag = Event()
        self._last_after = None

    def fight(self):
        if not self.flag.is_set():
            Thread(target=self.combat_loop, daemon=True).start()
            self.fight_button.config(text='STOP TEST')
        else:
            self.flag.clear()
            self.fight_button.config(text='RUN TEST')

    def combat_loop(self):
        self.flag.set()
        while True:
            for key in ['1', '2', '3', '4', '5']:
                self.autoclicker.press(key)
                self.autoclicker.wait(0.1)
                if not self.flag.is_set():
                    return

    def _reset(self):
        self.updater.reset()
        self.connect_button.config(state='normal')

    def _start_updating(self):
        self.updater.start()

    def _stop_updating(self):
        self.updater.stop()

    def reset(self):
        Thread(target=self._reset).start()

    def start_updating(self):
        Thread(target=self._start_updating).start()
        self.connect_button.config(text='STOP', command=self.stop_updating)
        self.reset_button.config(state='disabled')
        self.save_button.config(state='disabled')

    def stop_updating(self):
        Thread(target=self._stop_updating).start()
        self.connect_button.config(state='disabled', text='START', command=self.start_updating)
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
        self.after()
        self.mainloop()

    def save(self):
        Thread(target=self.updater.character.save).start()

    def quit(self):
        # self.root.after_cancel(self._last_after)
        self.root.destroy()




