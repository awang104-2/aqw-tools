from tkinter import *
from bot import Bot


class Interface:

    def __init__(self, routine=['1', '2', '3', '4', '5']):
        self.root = Tk()
        self.root.title('AQW Autoclicker')
        self.root.attributes('-topmost', True)
        self.root.geometry('200x180+50+50')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.label = Label(self.frame, text='N/A', font=('impact', 40, 'bold'))
        self.button = Button(self.frame, text='START', font=('Arial', 20, 'bold'), command=self.button_command)
        self.label.grid(row=0, column=0, sticky='nsew')
        self.button.grid(row=1, column=0, padx=30, pady=10)
        self.bot = Bot(routine=routine)
        self.running = False
        self.root.mainloop()

    def action(self):
        if not self.running:
            return
        dt = 100
        self.bot.action()
        self.root.after(dt, self.action)

    def button_command(self):
        if not self.running:
            self.running = True
            self.button.config(text='STOP')
            self.action()
        else:
            self.running = False
            self.button.config(text='START')
            self.action()


if __name__ == '__main__':
    Interface(routine=['2', '3', '4'])
