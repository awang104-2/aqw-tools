from src.v2.autoclicker import AutoClicker
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
        self.combat_params = {'routine': ['1', '2', '3', '4', '5'], 'delay': 0.25, 'status': True}
        self.quest_params = {'delays': [0.8, 0.8, 0.5, 0.2, 0.5, 0.5, 0.2], 'status': True}
        self.collector_params = {'confidence': 0.8, 'delay': 1.5, 'status': True}
        self.autoclicker = AutoClicker()
        self.hwnd = self.autoclicker.get_hwnd()

    def fight(self):
        try:
            self.autoclicker.press(self.combat_params['routine'][0])
            self.combat_params['routine'] = self.combat_params['routine'][1:] + [self.combat_params['routine'][0]]
            sleep(self.combat_params['delay'])
        except Exception as e:
            self.bot.running = False
            self.combat_params['status'] = False
            raise e

    def do_quest(self):
        try:
            step = 0
            while step < len(self.quest_params['delays']):
                delay = self.quest_params['delays'][step]
                match step:
                    case 0:
                        self.autoclicker.press('l')
                    case 1:
                        self.autoclicker.click((604, 263))
                    case 2:
                        img1 = get_screenshot_of_window(self.hwnd)
                        img2 = load_image(paths['turn in'])
                        top_left, bottom_right, _ = find_best_match(img1, img2, region=(0, 0, 900, 900))
                        coordinates = ((top_left + bottom_right) / 2).astype(int)
                        self.autoclicker.click(coordinates)
                    case 3:
                        img1 = get_screenshot_of_window(self.hwnd)
                        img2 = load_image(paths['number'])
                        top_left, bottom_right, max_val = find_best_match(img1, img2, region=(400, 300, 800, 800))
                        if max_val > 0.7:
                            coordinates = ((top_left + bottom_right) / 2).astype(int)
                            self.autoclicker.click(coordinates)
                        else:
                            step += 1
                    case 4:
                        self.autoclicker.type('9999')
                    case 5:
                        img1 = get_screenshot_of_window(self.hwnd)
                        img2 = load_image(paths['yes'])
                        top_left, bottom_right, max_val = find_best_match(img1, img2)
                        coordinates = ((top_left + bottom_right) / 2).astype(int)
                        self.autoclicker.click(coordinates)
                    case 6:
                        self.autoclicker.press('l')
                step += 1
                sleep(delay)
        except Exception as e:
            self.bot.running = False
            self.quest_params['status'] = False
            raise e

    def collect_items(self):
        try:
            img1 = get_screenshot_of_window(self.hwnd)
            img2 = load_image(paths['relic'])
            top_left, bottom_right, max_val = find_best_match(img1, img2)
            if max_val >= self.collector_params['confidence']:
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                coordinates[0] += 250
                self.autoclicker.click(coordinates)
        except Exception as e:
            self.bot.running = False
            self.collector_params['status'] = False
            raise e

    def exit_game(self):
        self.autoclicker.clear()
        sleep(3)
        self.autoclicker.quit_client()


class Overlay:

    def __init__(self, bot):
        # Interactions with Bot
        self.bot = bot

        # Fullscreen window overlay
        self.root = Tk()
        self.root.protocol('WM_DELETE_WINDOW', self.exit)
        self.root.attributes('-topmost', True)
        self.root.resizable(False, False)
        self.root.geometry('400x250+1400+20')
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Frame for window
        self.frame = Frame(self.root, background='purple')
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.frame.rowconfigure(list(range(100)), weight=1)
        self.frame.columnconfigure(list(range(100)), weight=1)

        # Widgets
        self.labels = {
            'status label': Label(master=self.frame, text='Status:', font=('arial', 25, ''), background='white'),
            'status': Label(master=self.frame, text='Offline', font=('arial', 25, ''), foreground='red', background='white')
        }
        self.buttons = {
            'stop': Button(master=self.frame, command=self.stop, text='STOP', font=('arial', 20, 'bold'), background='white', borderwidth=10)
        }
        self.labels['status label'].grid(row=40, column=49, sticky='ew')
        self.labels['status'].grid(row=40, column=50, sticky='ew')
        self.buttons['stop'].grid(row=98, column=49, columnspan=2, sticky='nsew', padx=10, pady=42)

    def __call__(self):
        # Update
        self.update()

        # Mainloop
        self.root.mainloop()

    def update(self):
        if self.bot.time['time'] > self.bot.time['time limit']:
            self.bot.running = False
            self.stop()
        elif self.bot.running:
            self.labels['status'].config(text='Online - ' + str(int(self.bot.time['time'])) + 's', foreground='#20C20E')
            self.bot.time['time'] += 0.1
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
        self.time = {'time': 0, 'time limit': int(60 * 60 * 1.5)}
        self.running = False

    def launch_overlay(self):
        self.overlay()
        print('Overlay ended.')

    def launch_routine(self):
        step, step_max = (0, int(4 * 60 * 3.3))
        while self.running:
            if step < step_max:
                self.player.fight()
                step += 1
            else:
                self.player.collect_items()
                self.player.do_quest()
                step = 0
        if self.time['time'] >= self.time['time limit']:
            self.player.exit_game()
        print('Routine ended.')

    def run(self):
        self.running = True
        side = Thread(target=self.launch_routine)
        main = Thread(target=self.launch_overlay)
        side.start()
        main.run()
        side.join()
        print('All threads joined.')


if __name__ == '__main__':
    bot = Bot()
    bot.run()
    print('Ended.')
