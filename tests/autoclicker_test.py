from bot.autoclicker import AutoClicker
from tkinter import *
import time


def window(autoclicker):
    root = Tk()
    root.geometry(f'{int(450*1.5)}x{int(250*1.5)}+0+0')
    label = Label(root)
    label.pack()
    action(root, label, 0, autoclicker)
    mainloop()


def action(root, label, count, autoclicker):
    count += 1
    label.config(text=f'{count}')
    autoclicker.press(f'{count % 5 + 1}')
    root.after(100, action, root, label, count, autoclicker)


def main():
    autoclicker = AutoClicker()
    autoclicker.connect()
    window(autoclicker)


if __name__ == '__main__':
    print('Test started.')
    main()
    print('Test finished.')
