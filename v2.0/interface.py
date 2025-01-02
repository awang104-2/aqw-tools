from tkinter import *
from bot import Bot
from threading import Thread


class Interface:

    def __init__(self):
        self.bot = None

        self.root = Tk()
        self.root.title('AQW Autoclicker')
        self.root.attributes('-topmost', True)
        self.root.geometry('700x500+560+200')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.label = Label(self.frame, text='Preferences', font=('impact', 40, 'bold'))
        self.button = Button(self.frame, text='START', font=('impact', 20, 'bold'), command=self.make_bot)
        self.label.grid(row=0, column=0, sticky='nsew')
        self.button.grid(row=1, column=0, padx=30, pady=10)
        self.root.mainloop()

    def make_bot(self):
        self.bot = Bot()


if __name__ == '__main__':
    Interface()
