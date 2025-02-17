# region ----- Import packages -----
import os
from numpy import gradient, floor, where, unique, max
import openpyxl
from scipy.constants import epsilon_0
import matplotlib.pyplot as plt
import pickle
from scipy.signal import savgol_filter
from Utilities.signal_processing import *
from Objects.measurement import FET, Figure
import matplotlib # endregion

"""
#######################################################################
    Author:         Davide Beretta
    Date:           07.01.2022
    Description:    IV plotter
#######################################################################
"""

# region ----- User inputs -----
main = r"T:"                # main_path directory
devices2load = ["ad", "af",
                "bf",
                "cd", "ce", "cg", "ch",
                "df", "dg", "dh", "di",
                "fd", "ff", "fg",
                "gc", "gi",
                "hd", "hf", "hi",
                "if", "ii",
                "je",
                "kg",
                "ld", "le", "lh",
                "mc", "me", "mf",
                "nd", "nf", "nh",
                "od",
                "pi",
                "qd", "qf", "qi"]
data2load = [("qd_gr_00", devices2load)]  # list of tuples, where the 1st element is the chip name, the 2nd is the device list
cycle_vds = 0           # [int] i-th Vds cycle to filter
sweep_vds = 2           # [int] direction of the Vds sweep to filter: {0: all, 1: fwd, 2: bkw}
smooth_window = 20/100  # [float] windon to smooth (in % of array lenght)
smooth_order = 3        # [int] order of the polynomial used to smooth
filter_d = [50]
plot00 = True           # [bool] plot IV traces
plot01 = True           # [bool] plot IV traces normalized
plot02 = True           # [bool] plot asymmetri [I(V) - I(-V)] / I(V)

# endregion

# region
# arc = pd.read_excel(rf"D:\My Drive\Work\Scripts\Python\Lab scripts\Chips\{fet.architecture}.xlsx")
# mat = pd.read_excel(rf"D:\My Drive\Work\Scripts\Python\Lab scripts\Chips\materials.xlsx")
# endregion

# region initialize figures
n = sum([len(x[1]) for x in data2load])
plot0 = Figure.PlotLine(xlabel="V (V)", ylabel="I (A)", obs=, semilogy=False)
plot1 = Figure.PlotLine(xlabel="V (V)", ylabel="I (A)", obs=, semilogy=False)
cm = matplotlib.cm.get_cmap("RdYlBu_r")
norm = matplotlib.colors.Normalize(5, 50)
device_dic = {'a': 5, 'b': 5, 'c': 5, 'd': 10, 'e': 10, 'f': 15, 'g': 15, 'h': 20, 'i': 20, 'j': 20, 'k': 25, 'l': 25,
              'm': 30, 'n': 30, 'o': 50, 'p': 50, 'q': 50}
color_dic = {5: cm(norm(0)), 10: cm(norm(1)), 15: cm(norm(2)), 20: cm(norm(3)), 25: cm(norm(4)), 30: cm(norm(5)), 50: cm(norm(6))}
marker_dic = {5: 'o', 10: 'o', 15: 'o', 20: 'o', 25: 'o', 30: 'o', 50: 'o'}
m = 0
# endregion


for chip_devices in data2load:  # run over the (chip, [devices]) tuples to load

    chip = chip_devices[0]
    devices = chip_devices[1]

    for device in devices:  # run over the devices to load

        experiments = os.listdir(rf"{main}\{chip}\{device}\iv")
        experiments = [x for x in experiments if x.endswith(".data")]

        if device_dic[device[0]] in filter_d:

            for experiment in experiments:  # run over the experiments to load

                # region ----- Load files -----
                path = rf"{main}\{chip}\{device}\iv\{experiment}"
                with open(path, "rb") as file:
                    fet = pickle.load(file)
                # endregion

                # region ----- Filter data -----
                fet.data.data = FET.Sweep.filter_vds_cycle(fet.data, cycle_vds)
                if sweep_vds == 0:
                    pass
                if sweep_vds == 1 and fet.data.data.shape[1] > 1:
                    fet.data.data = fet.data.data = FET.Sweep.filter_vds_fwd_sweep(fet.data)
                elif sweep_vds == 2 and fet.data.data.shape[1] > 1:
                    fet.data.data = fet.data.data = FET.Sweep.filter_vds_bkw_sweep(fet.data)
                # endregion

                # region ----- Process data -----
                x = fet.data.data[:, :, 2]
                y = fet.data.data[:, :, 3]
                # endregion

                if plot00 is True:
                    plot0.ax0.lines[m].set_data(x, y)
                    plot0.ax0.lines[m].set_color(cm(norm(device_dic[device[0]])))
                    plot0.ax1.lines[m].set_data(x, abs(y))
                    plot0.ax1.lines[m].set_color(cm(norm(device_dic[device[0]])))
                    plot0.ax0.relim()
                    plot0.ax0.autoscale_view(["x", "y"])
                    plot0.ax1.relim()
                    plot0.ax1.autoscale_view(["x", "y"])

                if plot01 is True:

                if plot

                m = m+1

# plot0.ax0.legend()
plt.show()
