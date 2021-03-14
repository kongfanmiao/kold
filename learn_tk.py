from tkinter import *

root = Tk()
frame1 = Frame(root)
frame2 = Frame(root)
var = StringVar()
var.set("I am coding")

def callback():
    var.set("I am hungry")

label = Label(frame1, textvariable=var, justify=LEFT)
label.pack(side=LEFT)
photo = PhotoImage(file='oxnanospin.png')
imglabel = Label(frame1, image=photo)
imglabel.pack(side=RIGHT)

thebutton = Button(frame2, text='It is 2 pm', command=callback)
thebutton.pack()
frame1.pack(padx=10, pady=10)
frame2.pack(padx=10, pady=10)

options = ['StabilityDiagram', 'GateTrace']
v = []
for op in options:
    v.append(IntVar())
    c = Checkbutton(root, text=op, variable=v[-1])
    c.pack()
l = Label(frame2, textvariable=str(v))
l.pack()

mainloop()
