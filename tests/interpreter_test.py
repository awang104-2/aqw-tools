from game.updater import Updater
from game.character import Character
from bot.autoclicker import AutoClicker
from tkinter import Tk, Label, Button
from queue import Queue


BASE_DPI = 96
ON = b'ENABLED'
OFF = b'DISABLED'
commands = Queue()


def get_dpi_scaling(root):
    dpi = root.winfo_fpixels('1i')
    return round(dpi/BASE_DPI, 3)


def stop(button, interpreter):
    global commands
    commands.put(OFF)


def start(button, interpreter):
    global commands
    commands.put(ON)


def window(interpreter, character):
    root = Tk()
    scaling_factor = get_dpi_scaling(root)
    root.geometry(f'{int(450 * scaling_factor)}x{int(250 * scaling_factor)}+0+0')
    root.attributes('-topmost', True)
    class_label = Label(root, font=("Arial", 20, "bold"))
    class_info = Label(root, font=("Arial", 10, "normal"))
    class_label.pack()
    class_info.pack()
    start_stop = Button(root, text='STOP', command=lambda: stop(start_stop, interpreter))
    start_stop.pack()
    autoclicker = AutoClicker()
    autoclicker.connect()
    periodic_check(root, class_label, class_info, start_stop, character, interpreter, autoclicker)
    root.mainloop()


def periodic_check(root, name, info, button, character, interpreter, autoclicker=None, count=0):
    if not commands.empty():
        cmd = commands.get()
        if cmd == ON:
            interpreter.reset_button()
            interpreter.connect()
            interpreter.start()
            button.config(text='STOP', command=lambda: stop(button, interpreter))
            button.update_idletasks()
        elif cmd == OFF:
            try:
                interpreter.stop()
                interpreter.disconnect()
            except RuntimeError:
                interpreter.stop()
                interpreter.force_quit()
            interpreter.join()
            button.config(text='START', command=lambda: start(button, interpreter))
            button.update_idletasks()
    if autoclicker and autoclicker.connected():
        autoclicker.press(f'{count % 5 + 1}')
        count += 1
    text = character.get_class_name()
    name.config(text=text)
    text = f'{character.get_skills_as_str()}\n{character.total_data_as_str()}\n\nSniffer Connected: {interpreter.connected('sniffer')}\nProcessor Connected: {interpreter.connected('processor')}'
    info.config(text=text)
    root.after(100, periodic_check, root, name, info, button, character, interpreter, autoclicker, count)


def main():
    import time
    character = Character()
    interpreter = Updater(server='twig', character=character, daemon=True)
    for i in range(5):
        interpreter.connect()
        print('start')
        interpreter.start()
        time.sleep(0.01)
        print('disconnecting')
        interpreter.disconnect()
        print('stopped')
        interpreter.stop()
        print('reset')
        interpreter.reset()


if __name__ == '__main__':
    main()