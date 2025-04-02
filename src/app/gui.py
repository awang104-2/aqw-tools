from tkinter import Tk, Frame, Label, Button, OptionMenu, StringVar
from packets.sniffing import AqwPacketLogger
from bot.player import AutoPlayer


def get_resolution():
    root = Tk()
    width, height = root.winfo_screenwidth(), root.winfo_screenheight()
    root.destroy()
    return str(width) + 'x' + str(height)


class Menu:

    def __init__(self):
        self.root = Tk()
        self.frame = Frame(self.root)
        self.server = StringVar(self.frame)
        self.server_menu = None
        self.label = Label(self.frame)
        self.button = Button(self.frame)
        self.bot = None

    def draw(self):
        self.root.geometry('500x400')
        self.root.attributes('-topmost', True)
        self.frame.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.configure_frame()

        self.label.config(text='Servers', font=('arial', 20, 'bold'), bg='lightblue')
        self.button.config(text='Start', command=self.selection)
        self.configure_option_menu()

        self.label.grid(row=1, column=2, pady=5, sticky='nsew')
        self.button.grid(row=3, column=2, pady=5, sticky='nsew')
        self.server_menu.grid(row=2, column=2, pady=5, sticky='nsew')

    def configure_option_menu(self):
        self.server.set('Select a Server')
        server_list = AqwPacketLogger.get_server_names()
        self.server_menu = OptionMenu(self.frame, self.server, *server_list)

    def configure_frame(self):
        # Background
        self.frame.config(bg='lightblue')

        # Rows
        self.frame.rowconfigure(0, weight=1)  # Empty space on the left
        self.frame.rowconfigure(1, weight=1)  # Content column 1
        self.frame.rowconfigure(2, weight=1)  # Content column 2
        self.frame.rowconfigure(3, weight=1)  # Content column 3
        self.frame.rowconfigure(4, weight=1)  # Empty space on the right

        # Columns
        for i in range(5):
            self.frame.columnconfigure(i, weight=1)

    def selection(self):
        server = self.server.get()
        if self.bot and self.bot.running():
            return
        try:
            resolution, quests = get_resolution(), ['supplies to spin the wheel of chance']
            self.bot = AutoPlayer(resolution=get_resolution(), quests=quests, server=server)
            self.bot.start()
            self.button.config(text='Stop', command=self.stop_bot)
        except ValueError:
            return

    def run(self):
        self.draw()
        self.root.mainloop()

    def stop_bot(self):
        if self.bot and self.bot.running:
            self.bot.stop()
            print('Drops -', self.bot.get_drops())
            print('Inventory -', self.bot.get_inventory())
            print()
            self.bot = None
        self.button.config(text='Start', command=self.selection)







