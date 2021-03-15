path = 'C:\\data\\Test\\dummy chip\\dumy device\\Test__dummy chip__dumy device__Vg-5000to5000__Vsd-20to20.csv'

import matplotlib.pyplot as plt
from qcodes.dataset.data_export import reshape_2D_data

from simulator import *


plt.figure(figsize=(6,4))
Vg, Vsd, current = get_data_from_csv(path)
x, y, z = reshape_2D_data(Vg, Vsd, current)
im = plt.pcolormesh(x,y,z,cmap='inferno')
cb = plt.colorbar(im)

def animate(i):
    global Vg, Vsd, current, cb, im
    Vg, Vsd, current = get_data_from_csv(path)
    cb.remove()
    im.remove()
    x, y, z = reshape_2D_data(Vg, Vsd, current)
    im = plt.pcolormesh(x,y,z,cmap='inferno')
    cb = plt.colorbar(im)

ani = animation.FuncAnimation(plt.gcf(), animate, interval=500)



