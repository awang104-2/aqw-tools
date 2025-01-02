from autoclicker import AutoClicker
from handlers.ImageHandler import *
from tkinter import *
from threading import Thread


paths = {
    'complete': '../assets/quest/general/complete.png',
    'relic': '../assets/quest/supplies/relic_of_chaos.png',
    'log complete': '../assets/quest/general/log_complete.png',
    'turn in': '../assets/quest/general/turn_in.png',
    'number': '../assets/quest/general/quest_number.png',
    'yes': '../assets/quest/general/yes.png'
}


class ActionManager:

    def __init__(self):
        self.combat_params = {'routine': ['1', '2', '3', '4', '5'], 'step': 0, 'delay': 250}
        self.quest_params = {'delay': 1000, 'step': 0}
        self.collector_params = {'confidence': 0.8, 'delay': 500}
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
            case 1:
                img1 = get_screenshot_of_window(self.hwnd, (0, 0, 900, 900))
                img2 = load_image(paths['turn in'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
            case 2:
                img1 = get_screenshot_of_window(self.hwnd)
                img2 = load_image(paths['number'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
            case 3:
                img1 = get_screenshot_of_window(self.hwnd)
                img2 = load_image(paths['yes'])
                top_left, bottom_right, _ = find_best_match(img1, img2)
                coordinates = ((top_left + bottom_right) / 2).astype(int)
                self.autoclicker.click(coordinates)
            case 4:
                self.quest_params['step'] = (self.quest_params['step'] + 1) % 5
                return self.quest_params['period']
        self.quest_params['step'] = (self.quest_params['step'] + 1) % 5
        return self.quest_params['delay']

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
        self.root.attributes('-fullscreen', True)
        self.root.configure(background='purple')
        self.root.wm_attributes('-transparentcolor', 'purple')

        # Frame for window
        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(3, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # Widgets
        self.labels = {
            'status label': Label(text='Status: ', font=('arial', 15, '')),
            'status': Label(self.frame, text='Offline', font=('arial', 15, ''), foreground='red')
        }
        self.buttons = {
            'stop': Button(self.frame, command=self.stop, text='STOP', font=('arial', 15, 'bold'))
        }
        self.labels['status label'].pack()

        # Update


        # Mainloop
        self.root.mainloop()

    def stop(self):
        self.root.after(3 * 1000, self.root.destroy)
        self.bot.running = False


class Bot:

    def __init__(self):
        self.bot = ActionManager()
        self.time = 0
        self.running = True

        self.root = Tk()
        self.root.title('AQW Autoclicker')
        self.root.attributes('-topmost', True)
        self.root.geometry('350x180+1500+10')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)





        for index, (key, label) in enumerate(self.status.items()):
            label.pack(anchor='center', pady=2)

        self.button = Button(self.frame, text='STOP', font=('Arial', 15, 'bold'), command=self.button_command)
        self.button.pack(anchor='center')

        self.actions = self.run_threads()

        self.root.mainloop()

    def combat_action(self):
        if not self.running:
            self.status['combat'].config(text='Combat Status: Stopped', foreground='red')
            return
        self.status['combat'].config(text='Combat Status: Running', foreground='#20C20E')
        dt = self.bot.fight()
        self.root.after(dt, self.combat_action)

    def quest_action(self):
        if not self.running:
            self.status['quest'].config(text='Quest Status: Stopped', foreground='red')
            return
        self.status['quest'].config(text='Quest Status: Running', foreground='#20C20E')
        dt = self.bot.do_quest()
        self.root.after(dt, self.quest_action)

    def collector_action(self):
        if not self.running:
            self.status['collector'].config(text='Collector Status: Stopped', foreground='red')
            return
        self.status['collector'].config(text='Collector Status: Running', foreground='#20C20E')
        dt = self.bot.collect_items()
        self.root.after(dt, self.collector_action)

    def run_threads(self):
        t2 = Thread(target=self.collector_action)
        t1 = Thread(target=self.quest_action)
        t3 = Thread(target=self.combat_action)

        threads = [t1, t2, t3]
        for index, t in enumerate(threads):
            t.start()
        return threads

    def button_command(self):
        if self.running:
            self.running = False
            self.root.after(10 * 1000, self.root.destroy)
            for index, action in enumerate(self.actions):
                action.join()



if __name__ == '__main__':
    Bot()






