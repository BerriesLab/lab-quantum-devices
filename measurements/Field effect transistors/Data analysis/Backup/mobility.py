# region ----- Import packages -----
import os
from numpy import gradient, unique, floor, flatnonzero
from scipy.constants import epsilon_0
import matplotlib.pyplot as plt
import pickle
from scipy.signal import savgol_filter
from Utilities.material_library import *
from Utilities.signal_processing import *
from Objects.Backup.measurement_objects import FET  # endregion

"""
#######################################################################
    Author:         Davide Beretta
    Date:           07.01.2022
    Description:    FET
    
    This script extract the FET mobility in a region o choice, either
    (0) in the linear region
    (1) in saturation
    (2) at the maximum slope of Ids vs Vgs 
#######################################################################
"""

# region ----- User inputs -----
main = r"R:\Scratch\405\dabe"                # main directory
data2load = [("tetra fet au p3ht", ["4wire h-20um"])]    # list of tuples, where the 1st element is the chip name, the 2nd is the device list
cycle_vgs = 0                       # [int] i-th Vgs cycle where to calculate mobility
cycle_vds = 0                       # [int] i-th Vds cycle where to calculate mobility
sweep_vgs = 0                       # [int] direction of the Vgs sweep where to extract the mobility: FWD ("0") or BWD ("1")
sweep_vds = 0                       # [int] direction of the Vds sweep where to extract the mobility: FWD ("0") or BWD ("1")
vds = []                            # [list of float] vds traces to consider. Pass empty list to include all
region = [0]                        # [list of int] region where to extract mobility: linear (0), saturation (1), max slope linear (2),
smooth_window = 10/100               # [float] windon to smooth (in % of array lenght)
smooth_order = 3                    # [int] order of the polynomial used to smooth
# endregion

plot0 = FET.PlotMobility(region)

for chip_devices in data2load:  # run over the (chip, [devices]) tuples to load

    chip = chip_devices[0]
    devices = chip_devices[1]

    for device in devices:  # run over the devices to load

        experiments = os.listdir(rf"{main}\{chip}\{device}\fet\vgs sweep")
        experiments = [x for x in experiments if x.endswith(".data")]

        for experiment in experiments:  # run over the experiments to load

            # region ----- Load file -----
            path = rf"{main}\{chip}\{device}\fet\vgs sweep\{experiment}"
            with open(path, "rb") as file:
                fet = pickle.load(file)
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

            # filter Vds Values
            if len(vds) != 0:
                data = data[any([data[k, 2] in vds for k in range(data.shape[0])]), :]
            # endregion

            for k, val in enumerate(unique(data[:, 2])):

                # region ----- Process data -----
                x = data[data[:, 2] == val][:, 0]
                y = data[data[:, 2] == val][:, 3]
                y_smooth = savgol_filter(y, int(2 * floor(smooth_window * len(x) / 2) + 1), smooth_order)    # smooth Ids
                # endregion

                # region ----- Calculate mobility -----
                if 0 in region:  # linear region
                    plot0.ax00.plot(x, y, "o")  # plot Ids vs Vgs raw
                    plot0.ax00.plot(x, y_smooth, "--")  # plot Ids smooth vs Vgs

                    dy_dx = gradient(y, x)  # calculate d(ids)/d(vgs) raw
                    dy_smooth_dx = gradient(y_smooth, x)  # calculate d(ids)/d(vgs) raw
                    c = epsilon_0 * material_library[data.oxide_material]["epsilon_r"] / data.oxide_thickness
                    mu_lin = data.channel_length / (data.channel_width * c * val) * dy_dx
                    mu_lin_smooth = data.channel_length / (data.channel_width * c * val) * dy_smooth_dx
                    plot0.ax1.plot(x, mu_lin, "o")                       # plot dy/dx raw
                    plot0.ax1.plot(x, mu_lin_smooth, "--")                # plot dy/dx raw

                if 1 in region:  # saturation region
                    sqrty = sqrt(abs(y))                            # calculate sqrt(Ids)
                    sqrty_smooth = sqrt(abs(y_smooth))              # smooth sqrt(Ids)
                    dsqrty_dx = gradient(sqrty, x)                  # calculate d(Ids)/d(Vgs)
                    dsqrty_smooth_dx = gradient(sqrty_smooth, x)    # calculate d(Ids smooth)/d(Vgs)
                    c = epsilon_0 * material_library[data.oxide_material]["epsilon_r"] / data.oxide_thickness
                    mu_sat = (2 * data.channel_length / (data.channel_width * c)) * dsqrty_dx
                    mu_sat_smooth = (2 * data.channel_length / (data.channel_width * c)) * dsqrty_smooth_dx
                    plot0.ax1.plot(x, mu_sat, "o")                  # plot dy/dx raw
                    plot0.ax1.plot(x, mu_sat_smooth, "--")          # plot dy/dx raw

                if 2 in region:  # max mobility
                    dy_dx = gradient(y, x)                          # calculate d(ids)/d(vgs) raw
                    dy_smooth_dx = gradient(y_smooth, x)            # calculate d(ids)/d(vgs) smooth
                    idx_max = flatnonzero(dy_smooth_dx == max(dy_smooth_dx))  # get idx at maximum d(ids)/d(vgs)
                    x_idx = flatnonzero((x <= x[idx_max] + 0.1 * max(x)) & (x >= x[idx_max] - 0.1 * max(x)))
                    x_tan = x[x_idx]
                    y_tan = y[idx_max] + dy_dx[idx_max] * (x_tan - x[idx_max])
                    y_tan_smooth = y_smooth[idx_max] + dy_smooth_dx[idx_max] * (x_tan - x[idx_max])
                    c = epsilon_0 * material_library[data.oxide_material]["epsilon_r"] / data.oxide_thickness
                    mu_lin = data.channel_length / (data.channel_width * c * val) * dy_dx[idx_max]
                    mu_lin_smooth = data.channel_length / (data.channel_width * c * val) * dy_smooth_dx[idx_max]
                    plot0.ax1.plot(x, y, "o")                            # plot Ids vs Vgs raw
                    plot0.ax1.plot(x_tan, y_tan, "-.")                    # plot tangent Ids vs Vgs raw
                    plot0.ax1.plot(x, y_smooth, "o")                     # plot Ids smooth vs Vgs
                    plot0.ax1.plot(x_tan, y_tan_smooth, "-.")             # plot tangent to Ids smooth vs Vgs
                # endregion

plt.show()
