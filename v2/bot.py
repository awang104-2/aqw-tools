from v2.autoclicker import AutoClicker
from handlers.ImageHandler import *
from tkinter import *
from threading import Thread
from time import sleep


paths = {
    'complete': '../assets/quest/general/complete.png',
    'relic': '../assets/quest/supplies/relic_of_chaos.png',
    'log complete': '../assets/quest/general/log_complete.png',
    'turn in': '../assets/quest/general/turn_in.png',
    'number': '../assets/quest/general/quest_number.png',
    'yes': '../assets/quest/general/yes.png'
}


class Player:

    def __init__(self, bot):
        self.bot = bot
        self.combat_params = {'routine': ['1', '2', '3', '4', '5'], 'step': 0, 'delay': 0.25}
        self.quest_params = {'delays': [0.8, 0.5, 0.2, 0.5, 0.2],  'step': 0}
        self.collector_params = {'confidence': 0.8, 'delay': 0.5}
        self.autoclicker = AutoClicker()
        self.hwnd = self.autoclicker.get_hwnd()

    def fight(self):
        self.autoclicker.press(self.combat_params['routine'][self.combat_params['step']])
        self.combat_params['step'] = (self.combat_params['step'] + 1) % len(self.combat_params['routine'])
        return self.combat_params['delay']

    def do_quest(self):
        match self.quest_params['step']:
            case 0:
                self.autoclicker.click((604, 263))
                self.quest_params['step'] = (self.quest_params['step'] + 1) % 5
                return self.quest_params['delays'][0]
            case 1:
                img1 = get_screenshot_of_window(self.hwnd)
                img2 = load_image(paths['turn in'])
                top_left, bottom_right, _ = find_best_match(img1, img2, region=(0, 0, 900, 900))
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
                self.quest_params['step'] = (self.quest_params['step'] + 1) % 5
                return self.quest_params['delays'][1]
            case 2:
                img1 = get_screenshot_of_window(self.hwnd)
                img2 = load_image(paths['number'])
                top_left, bottom_right, _ = find_best_match(img1, img2, region=(400, 300, 800, 800))
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
                self.quest_params['step'] = (self.quest_params['step'] + 1) % 5
                return self.quest_params['delays'][2]
            case 3:
                self.autoclicker.type('9999')
                self.quest_params['step'] = (self.quest_params['step'] + 1) % 5
                return self.quest_params['delays'][3]
            case 4:
                img1 = get_screenshot_of_window(self.hwnd)
                img2 = load_image(paths['yes'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
                self.quest_params['step'] = (self.quest_params['step'] + 1) % 5
                return self.quest_params['delays'][4]

    def collect_items(self):
        img1 = get_screenshot_of_window(self.hwnd)
        img2 = load_image(paths['relic'])
        top_left, bottom_right, max_val = find_best_match(img1, img2)
        if max_val >= self.collector_params['confidence']:
            coordinates = ((top_left + bottom_right) / 2).astype(int)
            coordinates[0] += 250
            self.autoclicker.click(coordinates)
        return self.collector_params['delay']


class Overlay:

    def __init__(self, bot):
        # Interactions with Bot
        self.bot = bot

        # Fullscreen window overlay
        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.exit)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(background='purple')
        self.root.wm_attributes('-transparentcolor', 'purple')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Frame for window
        self.frame = Frame(self.root, background='purple')
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.frame.rowconfigure(list(range(200)), weight=1)
        self.frame.columnconfigure(list(range(200)), weight=1)

        # Widgets
        self.labels = {
            'status label': Label(master=self.frame, text='Status:', font=('arial', 15, ''), background='white'),
            'status': Label(master=self.frame, text='Offline', font=('arial', 15, ''), foreground='red', background='white')
        }
        self.buttons = {
            'stop': Button(master=self.frame, command=self.stop, text='STOP', font=('arial', 15, 'bold'), background='white', borderwidth=10)
        }
        self.labels['status label'].grid(row=0, column=198, sticky='ew')
        self.labels['status'].grid(row=0, column=199, sticky='ew')
        self.buttons['stop'].grid(row=199, column=199, columnspan=2, sticky='nsew', padx=10, pady=42)

    def __call__(self):
        # Update
        self.update()

        # Mainloop
        self.root.mainloop()

    def update(self):
        if self.bot.running:
            self.labels['status'].config(text='Online', foreground='#20C20E')
            self.root.after(100, self.update)
        else:
            self.labels['status'].config(text='Offline', foreground='red')

    def exit_countdown(self):
        def display_time(time):
            msg = 'Exiting in ' + str(time) + '...'
            countdown.config(text=msg)

        countdown = Label(master=self.frame, text='', font=('arial', 40, 'bold'), foreground='red')
        countdown.grid(row=0, column=0, rowspan=200, columnspan=200, sticky='ew')
        self.root.after(0, lambda: display_time(3))
        self.root.after(1000, lambda: display_time(2))
        self.root.after(2000, lambda: display_time(1))

    def stop(self):
        self.bot.running = False
        self.exit_countdown()
        self.root.after(3000, self.root.destroy)

    def exit(self):
        self.bot.running = False
        self.root.destroy()


class Bot:

    def __init__(self):
        self.player = Player(self)
        self.overlay = Overlay(self)
        self.running = False

    def launch_overlay(self):
        self.overlay()

    def launch_routine(self):
        i, j, k = (0, 0, 0)
        while self.running:
            if i < 4 * 60 * 2.5:
                dt = self.player.fight()
                sleep(dt)
                i += 1
            elif j < 1:
                dt = self.player.collect_items()
                sleep(dt)
                j += 1
            elif k < 5:
                dt = self.player.do_quest()
                sleep(dt)
                k += 1
            else:
                i, j, k = (0, 0, 0)

    def run(self):
        self.running = True
        main = Thread(target=self.launch_overlay)
        side = Thread(target=self.launch_routine)
        side.start()
        main.run()
        side.join()
        print('Complete')


if __name__ == '__main__':
    bot = Bot()
    bot.run()
