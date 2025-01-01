from tkinter import *
from bot import Bot
from threading import Thread


class Interface:

    def __init__(self, routine=['1', '2', '3', '4', '5']):
        self.routine = routine
        self.status = 'Idle'
        self.bot = None
        self.time = 0
        self.running = False

        self.root = Tk()
        self.root.title('AQW Autoclicker')
        self.root.attributes('-topmost', True)
        self.root.geometry('300x150+1500+10')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.label = Label(self.frame, text=self.status, font=('impact', 40, 'bold'))
        self.button = Button(self.frame, text='START', font=('Arial', 20, 'bold'), command=self.button_command)
        self.label.grid(row=0, column=0, sticky='nsew')
        self.button.grid(row=1, column=0, padx=30, pady=10)
        self.root.mainloop()

    def combat_action(self):
        if not self.running:
            return
        dt = self.bot.fight()
        self.root.after(dt, self.combat_action)

    def quest_action(self):
        if not self.running:
            return
        dt = self.bot.do_quest()
        self.root.after(dt, self.quest_action)

    def item_action(self):
        if not self.running:
            return
        dt = self.bot.collect_items(confidence=0.7)
        self.root.after(dt, self.item_action)

    def clock(self):
        if not self.running:
            self.time = 0
            return
        string = self.status + ' - ' + str(self.time) + 's'
        self.label.config(text=string)
        self.time += 1
        self.root.after(1000, self.clock)

    def threads(self):
        t1 = Thread(target=self.clock)
        t2 = Thread(target=self.item_action)
        t3 = Thread(target=self.quest_action)
        t4 = Thread(target=self.combat_action)

        t1.start()
        t2.start()
        t3.start()
        t4.start()

    def button_command(self):
        if not self.running:
            self.running = True
            self.status = 'Battling'
            del self.bot
            self.bot = Bot(routine=self.routine)
            self.button.config(text='STOP')
            self.label.config(text=self.status, foreground='red')
            self.threads()
        else:
            self.running = False
            self.button.config(text='START')
            self.status = 'Idle'
            self.label.config(text=self.status, foreground='black')


if __name__ == '__main__':
    Interface(routine=['2', '3', '4', '5', '1'])
