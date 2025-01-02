import tkinter as tk

root = tk.Tk()
root.title('Tkinter Pack Layout')
root.geometry('600x400')

frame = tk.Frame(master=root, background='light blue')
frame.pack(fill='both')

label1 = tk.Label(master=frame, text='Tkinter', bg='red', fg='white')
label2 = tk.Label(master=frame, text='Pack Layout', bg='green', fg='white')
label3 = tk.Label(master=frame, text='Demo', bg='blue', fg='white')

label1.grid(row=0, column=0, sticky='nsew')
label2.grid(row=1, column=0, sticky='nsew')
label3.grid(row=2, column=0, sticky='nsew')

root.mainloop()