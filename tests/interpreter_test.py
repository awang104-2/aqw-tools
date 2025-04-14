from game.interpreter import Interpreter
from game.character import Character
from pynput.keyboard import Listener, Key
from tkinter import *


def on_release(key, interpreter, character):
    if key == Key.esc:
        interpreter.stop()
        interpreter.disconnect()
        interpreter.join()
        return False
    elif key == Key.ctrl_l:
        print(f'\n{character}\n')


def stop(interpreter, character):
    interpreter.stop()
    interpreter.disconnect()
    character.save('all')


def window(interpreter, character):
    root = Tk()
    root.geometry('400x300')
    label = Label(root)
    label.pack()
    start_stop = Button(root, text='STOP', command=lambda: stop(interpreter, character))
    start_stop.pack()
    display(label, character, interpreter)
    mainloop()


def display(label, character, interpreter):
    text = f'{character}\nSniffer Connected: {interpreter.connected('sniffer')}\nProcessor Connected: {interpreter.connected('processor')}'
    label.config(text=text)
    label.after(100, display, label, character, interpreter)


def main():
    character = Character()
    interpreter = Interpreter(server='twig', character=character, daemon=True)
    interpreter.connect()
    interpreter.start()
    window(interpreter, character)


if __name__ == '__main__':
    main()