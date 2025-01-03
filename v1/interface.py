from tkinter import *


class Interface(Tk):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.active_time = 0
        self.__init_window()
        mainloop()

    def __init_window(self):
        self.title('AQW Autoclicker')
        self.geometry('240x130+10+10')
        self.attributes('-topmost', True)
        self.__init_labels()
        self.__init_buttons()
        self.__init_listbox()

    def __init_buttons(self):
        string = None
        command = None
        if self.bot.running:
            string = 'Stop'
            command = self.__stop
        else:
            string = 'Start'
            command = self.__start
        self.start_stop = Button(self, command=command, text=string, width=10, height=1, font=('calibri', 20, 'bold'))
        self.start_stop.pack()

    def __init_listbox(self):
        pass

    def __init_labels(self):
        self.lbl = Label(self, font=('calibri', 30, 'bold'))
        self.lbl.config(text='0s')
        self.lbl.pack()

    def __start(self):
        self.bot.start()
        self.active_time = 0
        self.__time()
        self.start_stop.destroy()
        self.start_stop = Button(self, command=self.__stop, text='Stop', width=10, height=1, font=('calibri', 20, 'bold'))
        self.start_stop.pack()

    def __stop(self):
        self.lbl.config(text=str(self.active_time) + 's')
        self.bot.stop()
        self.start_stop.destroy()
        self.start_stop = Button(self, command=self.__start, text='Start', width=10, height=1, font=('calibri', 20, 'bold'))
        self.start_stop.pack()

    def __time(self):
        if self.bot.running:
            string = str(self.active_time) + 's' + ' (' + str(self.bot.timer) + 's)'
            self.bot.timer += 1
            self.active_time += 1
            self.lbl.config(text=string)
            self.lbl.after(1000, self.__time)

    def destroy(self):
        self.bot.stop()
        super().destroy()

