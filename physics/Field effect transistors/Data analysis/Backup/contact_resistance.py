# region ----- Import packages -----
import os
import matplotlib.pyplot as plt
import pickle
from scipy.stats import linregress
from Utilities.signal_processing import *
from Objects.measurement import FET  # endregion

"""
#######################################################################
    Author:         Davide Beretta
    Date:           07.01.2022
    Description:    extract contact resistance from IVs
    
    This script extract the contact resistance of a conducting channel,
    from the IVs of a set of devices having difference channel length 

#######################################################################
"""

# region ----- User inputs -----
main = r"T:"                # main directory
data2load = [("tetra fet au p3ht", ["4wire a-5um", "4wire b-10um"])]    # list of tuples, where the 1st element is the chip name, the 2nd is the device list
cycle_vgs = 0                       # [int] i-th Vgs cycle where to calculate mobility
cycle_vds = 0                       # [int] i-th Vds cycle where to calculate mobility
sweep_vgs = 0                       # [int] direction of the Vgs sweep where to extract the mobility: FWD ("0") or BWD ("1")
sweep_vds = 0                       # [int] direction of the Vds sweep where to extract the mobility: FWD ("0") or BWD ("1")
environment = [0]                   # [int] measurement environment {0: vacuum, 1: air, 2: N2, 3: Ar}
illumination = [0]                  # [int] illumination {0: dark, 1: light}
# endregion

# region ----- MAKE FIGURE -----
plot0 = FET.PlotContactResistance()
# endregion

rs = []
ls = []
for chip_devices in data2load:  # run over the (chip, [devices]) tuples to load

    chip = chip_devices[0]
    devices = chip_devices[1]

    for device in devices:  # run over the devices to load

        experiments = os.listdir(rf"{main}\{chip}\{device}\fet\iv")
        experiments = [x for x in experiments if x.endswith(".data")]

        for experiment in experiments:  # run over the experiments to load

            # region ----- Load file -----
            path = rf"{main}\{chip}\{device}\fet\iv\{experiment}"
            with open(path, "rb") as file:
                fet = pickle.load(file)
            if (fet.data.illumination not in illumination) or (fet.data.environment not in environment):
                continue
            data = fet.data.data
            data = data.reshape((data.shape[0]*data.shape[1], 7))
            # endregion

            # region ----- Filter data -----
            # filter cycles
            data = data[(data[:, 4] == cycle_vgs) & (data[:, 5] == cycle_vds)]

            # filter Vgs and Vds sweep direction (FWD or BWD)
            if sweep_vgs == 0:
                idx_vgs = non_decreasing_array(data[:, 0], 1)
            elif sweep_vgs == 1:
                idx_vgs = non_increasing_array(data[:, 0], 1)
            if sweep_vds == 0:
                idx_vds = non_decreasing_array(data[:, 2], 1)
            elif sweep_vds == 1:
                idx_vds = non_increasing_array(data[:, 2], 1)
            idx = idx_vgs * idx_vds
            data = data[idx, :]

            # region ----- Process data -----
            v = data[:, 2]
            i = data[:, 3]
            l = fet.data.channel_length
            w = fet.data.channel_width
            r = (1 / linregress(v, i)[0]) * w  # contact resistance * m

            ls.append(l)
            rs.append(r)

            plot0.ax0.plot(v, i, "o")                          # plot Ids vs Vgs raw
            plot0.ax1.plot(l*1e6, r, "o")                          # plot Ids vs Vgs raw
            # endregion

result = linregress(ls, rs)
linfitx = linspace(0, max(ls), 100)
plot0.ax1.plot(linfitx*1e6, result[1] + linfitx * result[0], "--")
plot0.ax1.plot(0, result[1], "o", color="black")
plt.annotate(f"{result[1]/1e3:.1f} k$\Omega$m",  # this is the text
             (0, result[1]), # these are the coordinates to position the label
             textcoords="offset points", # how to position the text
             xytext=(10,10), # distance from text to points (x,y)
             ha='left') # horizontal alignment can be left, right or center

plt.show()