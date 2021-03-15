import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from qcodes.dataset.data_export import reshape_2D_data


def plot_heatmap(x_raw, y_raw, z_raw, cmap='inferno',
                 figsize=(6, 4), **kwargs):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)
    x, y, z = reshape_2D_data(x_raw, y_raw, z_raw)
    im = ax.pcolormesh(x, y, z, cmap=cmap, **kwargs)
    plt.xlabel("Vg (V)")
    plt.ylabel("Vsd (mV)")
    plt.colorbar(im)


def plot_csv(path, skiprows: int, index_col=0, header=[0, 1], delimiter=',', **kwargs):
    Vg, Vsd, current = get_raw_data_from_csv(path, delimiter=delimiter, skiprows=skiprows,
                                             header=header, index_col=index_col)
    plot_heatmap(Vg, Vsd, current, **kwargs)


def get_raw_data_from_csv(path, skiprows, index_col=0, delimiter=',', header=[0, 1]
                          ):
    with open(path) as csv:
        df = pd.read_csv(csv, delimiter=delimiter, skiprows=skiprows,
                         header=header, index_col=index_col)
        current = df['current'].values
        Vsd = df['Vsd'].values
        Vg = df['Vg'].values
    return Vg, Vsd, current
