import tkinter as tk
from kold import *

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.run = tk.Button(self)
        self.run["text"] = "Run simulator"
        self.run["command"] = self.run_measurement
        self.run.pack()

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def run_measurement(self):
        exec(open('./kold/simulator.py').read())


root = tk.Tk()
root.title("Simulator Live Plotting")
root.geometry('500x300')
app = Application(master=root)
app.mainloop()