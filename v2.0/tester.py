from tkinter import *

Nx = 1
Ny = 2

root = Tk()
root.geometry('500x100+50+50')
frame = Frame(root)
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
frame.grid(row=0, column=0, sticky="nsew")

width = range(Nx)
height = range(Ny)
frame.columnconfigure(tuple(width), weight=1)
frame.rowconfigure(tuple(height), weight=1)

#example values
for x in range(Nx):
    for y in range(Ny):
        if y == 0:
            lbl = Label(frame, text='Label', font=('calibri', 40, 'bold'))
            lbl.grid(column=x, row=y, sticky='nsew')
        else:
            btn = Button(frame, text='Button')
            btn.grid(column=x, row=y, sticky="nsew", padx=10)

root.mainloop()
