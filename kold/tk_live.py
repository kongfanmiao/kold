path = 'C:\\data\\Test\\dummy chip\\dumy device\\Test__dummy chip__dumy device__Vg-5000to5000__Vsd-20to20.csv'

import matplotlib.pyplot as plt
from qcodes.dataset.data_export import reshape_2D_data

from simulator import *

# def tk_show(path):
fig = plt.figure(figsize=(6,4))
Vg, Vsd, current = get_data_from_csv(path)
x, y, z = reshape_2D_data(Vg, Vsd, current)
im = plt.pcolormesh(x,y,z,cmap='inferno')
cb = plt.colorbar(im)
window = tk.Tk()
window.title("Dynamic plotting")
window.geometry("500x500")

def animate(i):
    global Vg, Vsd, current, cb, im
    Vg, Vsd, current = get_data_from_csv(path)
    cb.remove()
    im.remove()
    x, y, z = reshape_2D_data(Vg, Vsd, current)
    im = plt.pcolormesh(x,y,z,cmap='inferno')
    cb = plt.colorbar(im)
    plt.xlabel("Vg (V)")
    plt.ylabel("Vsd (mV)")

canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack()
toolbar = NavigationToolbar2Tk(canvas, window)
toolbar.update() 
canvas.get_tk_widget().pack()

def quit():
    global window  
    window.destroy()

tk.Button(window, text='Quit', command=quit).pack()
ani = animation.FuncAnimation(fig, animate, interval=1000)
window.mainloop()


    # if __name__ == '__main__':
    #     tk_show(path)