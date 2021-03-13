from qcodes.dataset import plotting
from qcodes.dataset.data_export import reshape_2D_data
from nicola.ivvi_measure import Vsd_divider
import qcodes
from qcodes.station import Station
from qcodes.dataset import Measurement
from qcodes.instrument.parameter import Parameter
from qcodes.dataset.plotting import plot_dataset
from ..sample import Sample, Chip, Device
from ..instrument_drivers import *

from typing import Union
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import os


class BaseMeasurement(Measurement):
    """
    Base class for kold measurements
    """

    def __init__(self, experiment, station: Station, device: Device,
                 name=""):
        super().__init__(experiment, station, name)
        self.device = device
        self.file_path = self.device.path
        self.instruments = self.station.components

        for name, instr in self.instruments.items():
            setattr(self, name, instr)
        if not hasattr(self, 'triton'):
            raise RuntimeError("Please add Triton to the station")
        if not hasattr(self, 'alazar'):
            raise RuntimeError("Please add Alazar to the station")
        if not hasattr(self, 'ivvi'):
            raise RuntimeError("Please add IVVI to the station")
        self.triton: Triton
        self.alazar: AlazarATS9440
        self.ivvi: IVVI
        

    def print_info(self):
        pass

    def log_data(self, dataset):
        pass

    def get_meas_name(self):
        pass

        



class StabilityDiagram(BaseMeasurement):
    def __init__(self, experiment, station: Station, device, name=""):
        super().__init__(experiment, station, device, name)
        self.meas_type = "SD"
        self.live_plot_figsize = (10,6)
        self.cmap = 'inferno'

        # register measurement parameters
        self.register_parameter(self.ivvi.dac1)
        self.register_parameter(self.ivvi.dac2)
        self.register_parameter(self.triton.MC)
        self.current = Parameter(name='current',
                                       label='Source-Drain Current',
                                       unit='A')
        self.timestamp = Parameter(name='timestamp',
                                label='Timestamp',
                            unit='s')
        self.register_parameter(self.current, paramtype='array')
        self.register_parameter(self.timestamp, paramtype='array')

    def configure_plotting(self, **kwargs):
        if 'figsize' in kwargs.keys():
            self.live_plot_figsize = kwargs['figsize']
        if 'cmap' in kwargs.keys():
            self.cmap = kwargs['cmap']




    def set_parameters(self, Vg_range: Union[tuple, list],
                       Vsd_range: Union[tuple, list],
                       integration_time: float,
                       Vg_gain: float = 5e-3,
                       current_gain: float = 1e6,
                       Vsd_divider: float = 0.1,
                       Vg_npts: int = 20*16,
                       Vsd_npts: int = 20*16,
                       Vg_ramp_to_zero: bool = False, 
                       gate_sleep: int = 10):
        self.params = locals()
        self.name = self.get_meas_name()
        self.csv_file_name = self.name + '.csv'
        self.csv_path = os.path.join(self.device.path,
            self.csv_file_name)
        return self.params
        

    def get_meas_name(self):
        vgf, vgl = self.params['Vg_range'] # Vg first and last value
        vsdf, vsdl = self.params['Vsd_range']  # Vsd first and last
        name = "__".join((self.device.sample.name,
                          self.device.chip.name,
                          self.device.name,
                          self.meas_type,
                          f"Vg{vgf*1000}to{vgl*1000}",
                          f"Vsd{vsdf}to{vsdl}"))
        return name

    def start_run(self):
        
        vgf, vgl = self.params['Vg_range'] # Vg first and last value
        vsdf, vsdl = self.params['Vsd_range']  # Vsd first and last
        Vg_list = np.linspace(vgf, vgl, self.params['Vg_npts'])
        Vsd_list = np.linspace(vsdf, vsdl, self.params['Vsd_npts'])

        Vg_gain = self.params['Vg_gain']
        Vsd_divider = self.params['Vsd_divider']
        current_gain = self.params['current_gain']

        # clear memory of the Alazar card
        _ = self.alazar.controller.read()
        self.ivvi.dac1.set(vgf/self.params['Vg_gain'])

        # not sure how long time I should sleep here
        time.sleep(1)

        meas_counter = 0
        total_measures = len(Vg_list)
        tic1 = time.clock()
        
        headers = pd.MultiIndex.from_tuples(zip([
            'Vg', 'Vsd', 'Isd', 'MC_Temp', 'Timestamp'],
            ['V', 'mV', 'A', 'K', 's']))
        df_headers = pd.DataFrame(data=[], columns=headers)
        with open(self.csv_path, 'w') as cf:
            cf.write(f"""Parameters:
    Vg_range, {vgf} tp {vgl}
    Vsd_range, {vsdf} to {vsdl}
    integration_time, {self.params['integration_time']}
    Vg_gain, {Vg_gain}
    current_gain, {current_gain}
    Vsd_divider, {Vsd_divider}
    Vg_npts, {self.params['Vg_npts']}
    Vsd_npts, {self.params['Vsd_npts']}
    Vg_ramp_to_zero, {self.params['Vg_ramp_to_zero']}
    gate_sleep, {self.params['gate_sleep']}
""")
        with open(self.csv_path, 'r') as cf:
            param_lines = cf.readlines()
            self.rows_of_param_lines = len(param_lines)
        
        df_headers.to_csv(self.csv_path, mode='a', sep=',')

        vg_all = []
        vsd_all = []
        curr_all = []
        # plt.ioff()
        vg_gen = (vg for vg in Vg_list)
        fig = plt.figure(figsize=self.live_plot_figsize)
        ax = fig.add_subplot(111)
        # blank figure
        im = ax.pcolormesh([0,0],[0,0],[[0,0],[0,0]], cmap=self.cmap)
        cb = fig.colorbar(im)
        plt.xlabel("Vg (V)")
        plt.ylabel("Vsd (mV)")
        plt.title(f"{self.name}\n")

        with self.run() as datasaver:
            t0 = time.time()
            def animate(i):
                nonlocal cb, im, fig, ax
                try:
                    vg = next(vg_gen)
                    cb.remove()
                    im.remove()
                    self.ivvi.dac1(vg/Vg_gain)
                    meas_counter += 1
                    vg_temp = []
                    vsd_temp = []
                    curr_temp = []
                    mct_temp = []
                    tmstp_temp = []

                    for vsd in Vsd_list:
                        self.ivvi.dac2(vsd/Vsd_divider)
                        curr = self.alazar.read()
                        # divide the M1b module current gain or not?
                        MC_Temp = self.triton.MC()
                        t = time.time()
                        t_elap = t - t0
                        vg_temp.append(vg)
                        vsd_temp.append(vsd)
                        curr_temp.append(curr)
                        mct_temp.append(MC_Temp)
                        tmstp_temp.append(t_elap)
                        vg_all.append(vg)
                        vsd_all.append(vsd)
                        curr_all.append(curr)
                        
                        # save to database file
                        datasaver.add_result((self.ivvi.dac1, vg),
                                             (self.ivvi.dac2, vsd),
                                             (self.current, curr),
                                             (self.triton.MC, MC_Temp),
                                             (self.timestamp, t_elap))

                    # add a data block to csv file
                    data_temp = np.vstack(vg_temp,
                                          vsd_temp,
                                          curr_temp,
                                          mct_temp,
                                          tmstp_temp).T
                    df_temp = pd.DataFrame(data=data_temp)
                    df_temp.to_csv(self.csv_path, mode='a', sep=',', header=0)

                    # make live plot
                    x, y, z = reshape_2D_data(vg_all, vsd_all, curr_all)
                    im = ax.pcolormesh(x, y, z, cmap=self.cmap)
                    cb = fig.colorbar(im)

                    # print estimated completion time
                    t_now = time.time()
                    t_to_finish = (len(Vg_list)-meas_counter)*(
                        t_now-t0)/meas_counter
                    print("Estimated time to finish --> \
                         {:.0f} h {:.0f} min {:.0f} s".format(
                             t_to_finish//3600, t_to_finish//60, t_to_finish%60
                         ))
                except StopIteration:
                    # Vsd set to zero after sweeping
                    self.ivvi.dac2(0)
                    self.dataset = datasaver.dataset

            ani = animation.FuncAnimation(plt.gcf(), animate,
                                    interval=self.params['gate_sleep'])
            plt.show()

    def plot(self):
        plot_dataset(self.dataset)
        plt.title(f"{self.name}\n")
        plt.xlabel("Vg (V)")
        plt.ylabel("Vsd (mV)")

        

                        





        
        







