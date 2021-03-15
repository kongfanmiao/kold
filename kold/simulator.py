import os
import time
import numpy as np
import pandas as pd
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,\
    NavigationToolbar2Tk
from qcodes import Station, Measurement, Instrument, load_or_create_experiment,\
    initialise_or_create_database_at
from qcodes.dataset.plotting import plot_dataset
from qcodes.tests.instrument_mocks import DummyInstrument
from qcodes.dataset.data_export import reshape_2D_data
from kold.sample import Sample, Chip, Device



def generate_CD_curr(Vg, Vsd, width=2, slope=20, smear=0.1):
    """
    Generate Coulomb Diamond current
    """
    Vgn = Vg - width*np.floor((Vg+width/2)/width)
    temp = np.abs(Vgn) - np.abs(Vsd/slope)
    curr = 1/(1+np.exp(temp/smear))
    return curr
    
def load_or_create_dummy_instrument(name, **kwargs):
    if Instrument.exist(name):
        instr = Instrument.find_instrument(name)
        if Instrument.is_valid(instr):
            instrument = instr
        else:
            Instrument.close(instr)
            instrument = DummyInstrument(name, **kwargs)
    else:
        instrument = DummyInstrument(name, **kwargs)
    return instrument


class DummyStabilityDiagram(Measurement):

    def __init__(self, name="dummy stability diagram measurement"):
        super().__init__()
        self.sample = Sample(name='Test', log=False)
        self.chip = Chip('dummy chip', self.sample)
        self.device = Device('dumy device', self.sample, self.chip)

        # define the station and dummy instruments within class
        dac = load_or_create_dummy_instrument('dac', gates = ['Vg', 'Vsd'])
        dmm = load_or_create_dummy_instrument('dmm', gates = ['current'])
        self.station = Station(dac, dmm)
        self.dac, self.dmm = dac, dmm
        
        # initialise database, experiment
        self.device.create_database()
        self.experiment = load_or_create_experiment(
            experiment_name='test', sample_name=self.sample.name)
        self.register_parameter(self.dac.Vg)
        self.register_parameter(self.dac.Vsd)
        self.register_parameter(dmm.current, setpoints=(self.dac.Vg,
            self.dac.Vsd))

    def get_meas_name(self):
        vg1, vg2 = self.params['Vg_range']
        vsd1, vsd2 = self.params['Vsd_range']
        name = "__".join((self.sample.name,
                          self.chip.name,
                          self.device.name,
                          f"Vg{vg1*1000}to{vg2*1000}",
                          f"Vsd{vsd1}to{vsd2}"))
        return name

    def set_parameters(self, Vg_range, Vsd_range, width=2, slope=20, smear=0.1):
        self.params = dict(
            Vg_range=Vg_range,
            Vsd_range=Vsd_range,
            width=width,
            slope=slope,
            smear=smear
        )
        self.name = self.get_meas_name()

    def start_run(self, ami_show=True):
        print("Measurement starts")

        Vg_list = np.linspace(*self.params['Vg_range'], 100)
        Vsd_list = np.linspace(*self.params['Vsd_range'], 100)
        
        headers = pd.MultiIndex.from_tuples(zip(['Vg', 'Vsd', 'current'],
            ['V', 'mV', 'A']))
        df_headers = pd.DataFrame(data=[], columns=headers)
        self.csv_path = os.path.join(self.device.path, f'{self.name}.csv')

        vg1, vg2 = self.params['Vg_range']
        vsd1, vsd2 = self.params['Vsd_range']
        with open(self.csv_path, 'w') as cf:
            cf.write(f"""Parameters:
Vg range (V), {vg1} to {vg2}
Vsd range (mV), {vsd1} to {vsd2}
width, {self.params['width']}
slope, {self.params['slope']}
smear, {self.params['smear']}
""")
        df_headers.to_csv(self.csv_path, mode='a', sep=',')

        vg_all = []
        vsd_all = []
        curr_all = []
        plt.ioff()
        vg_gen = (vg for vg in Vg_list)
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111)
        im = ax.pcolormesh([0,0],[0,0],[[0,0],[0,0]], cmap='inferno')
        cb = fig.colorbar(im)
        plt.xlabel("Vg (V)")
        plt.ylabel("Vsd (mV)")
        plt.title(f"{self.name}\n")

        with self.run() as datasaver:
            def animate(i):
                nonlocal cb, im, fig, ax
                try:
                    vg = next(vg_gen)
                    cb.remove()
                    im.remove()
                    self.dac.Vg(vg)
                    vg_temp = []
                    vsd_temp = []
                    curr_temp = []
                    for vsd in Vsd_list:
                        self.dac.Vsd(vsd)
                        curr = generate_CD_curr(
                            Vg=vg, Vsd=vsd,
                            width=self.params['width'],
                            slope=self.params['slope'],
                            smear=self.params['smear']
                        )
                        vg_temp.append(vg)
                        vsd_temp.append(vsd)
                        curr_temp.append(curr)
                        vg_all.append(vg)
                        vsd_all.append(vsd)
                        curr_all.append(curr)
                        datasaver.add_result((self.dac.Vg, vg),
                                                (self.dac.Vsd, vsd),
                                                (self.dmm.current, curr))
                    data1 = np.vstack((vg_temp, vsd_temp, curr_temp)).T
                    df1 = pd.DataFrame(data=data1)
                    df1.to_csv(self.csv_path, mode='a', sep=',', header=0)
                    x, y, z = reshape_2D_data(vg_all, vsd_all, curr_all)
                    im = ax.pcolormesh(x,y,z,cmap='inferno')
                    cb = fig.colorbar(im)
                    # time.sleep(0.2)
                except StopIteration:
                    pass
                
            self.dataset = datasaver.dataset
            ani = animation.FuncAnimation(plt.gcf(), animate, interval=50)
            plt.show()
        
        

    
    def plot_ds(self):
        plot_dataset(self.dataset)
        plt.xlabel("Vg (V)")
        plt.ylabel("Vsd (mV)")


def plot_heatmap(x_raw, y_raw, z_raw, cmap='inferno',
                figsize=(6,4), **kwargs):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    x, y, z = reshape_2D_data(x_raw, y_raw, z_raw)
    im = ax.pcolormesh(x, y, z, cmap=cmap, **kwargs)
    plt.xlabel("Vg (V)")
    plt.ylabel("Vsd (mV)")
    plt.colorbar(im)

def plot_csv(path, skiprows=6, header=[0,1], index_col=0, delimiter=',', **kwargs):
    Vg, Vsd, current = get_data_from_csv(path, delimiter=delimiter, skiprows=skiprows,
                        header=header, index_col=index_col)
    plot_heatmap(Vg, Vsd, current, **kwargs)


def get_raw_data_from_csv(path, skiprows=6, delimiter=',', header=[0,1],
                      index_col=0):
    with open(path) as csv:
        df = pd.read_csv(csv, delimiter=delimiter, skiprows=skiprows,
                        header=header, index_col=index_col)
        current = df['current'].values
        Vsd = df['Vsd'].values
        Vg = df['Vg'].values
    return Vg, Vsd, current


if __name__ == '__main__':
    dsd = DummyStabilityDiagram()
    dsd.set_parameters([-5,5], [-20,20])
    dsd.start_run()