# region ----- Import packages -----
import os
from numpy import gradient, unique, floor, flatnonzero, loadtxt
import pandas as pd
from scipy.constants import epsilon_0
import matplotlib.pyplot as plt
import pickle
from scipy.signal import savgol_filter
from Utilities.signal_processing import *
from Objects.measurement import FET
import matplotlib # endregion

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
main = r"T:"                # main directory
data2load = [("tep_ch3_00", ["a1", "c3"]),
             ("tep_ch3_01", ["a1"]),
             ("tep_ch3_10", ["a1"]),
             ("tep_ch3_11", ["a2", "b1", "c1", "c2"])]  # list of tuples, where the 1st element is the chip name, the 2nd is the device list
cycle_vgs = 0           # [int] i-th Vgs cycle where to calculate mobility
cycle_vds = 0           # [int] i-th Vds cycle where to calculate mobility
sweep_vgs = 0           # [int] direction of the Vgs sweep where to extract the mobility: FWD ("0") or BWD ("1")
sweep_vds = 0           # [int] direction of the Vds sweep where to extract the mobility: FWD ("0") or BWD ("1")
vds = [1e-2]            # [list of float] vds traces to consider. Pass empty list to include all
region = [0]            # [list of int] region where to extract mobility: linear (0), saturation (1)
smooth_window = 25/100  # [float] windon to smooth (in % of array lenght)
smooth_order = 3        # [int] order of the polynomial used to smooth
# endregion

plot0 = FET.PlotMobility()
n = sum([len(x[1]) for x in data2load])
cm = matplotlib.cm.get_cmap("RdYlBu_r")
norm = matplotlib.colors.Normalize(0, n)
m = 0

for chip_devices in data2load:  # run over the (chip, [devices]) tuples to load

    chip = chip_devices[0]
    devices = chip_devices[1]

    for device in devices:  # run over the devices to load

        experiments = os.listdir(rf"{main}\{chip}\{device}\vgs sweep")
        experiments = [x for x in experiments if x.endswith(".data")]

        for experiment in experiments:  # run over the experiments to load

            # region ----- Load files -----
            path = rf"{main}\{chip}\{device}\vgs sweep\{experiment}"
            with open(path, "rb") as file:
                fet = pickle.load(file)
            arc = pd.read_excel(rf"D:\My Drive\Work\Scripts\Python\Lab scripts\Chips\{fet.architecture}.xlsx")
            mat = pd.read_excel(rf"D:\My Drive\Work\Scripts\Python\Lab scripts\Chips\materials.xlsx")
            # endregion

            # region ----- Filter data -----
            fet.data.data = FET.Sweep.filter_vgs_cycle(fet.data, cycle_vgs)
            fet.data.data = FET.Sweep.filter_vds_cycle(fet.data, cycle_vds)
            fet.data.data = FET.Sweep.filter_vds_values(fet.data, vds)
            if sweep_vgs == 0 and fet.data.data.shape[0] > 1:
                fet.data.data = fet.data.data = FET.Sweep.filter_vgs_fwd_sweep(fet.data)
            elif sweep_vgs == 1 and fet.data.data.shape[0] > 1:
                fet.data.data = fet.data.data = FET.Sweep.filter_vgs_bkw_sweep(fet.data)
            if sweep_vds == 0 and fet.data.data.shape[1] > 1:
                fet.data.data = fet.data.data = FET.Sweep.filter_vds_fwd_sweep(fet.data)
            elif sweep_vds == 1 and fet.data.data.shape[1] > 1:
                fet.data.data = fet.data.data = FET.Sweep.filter_vds_bkw_sweep(fet.data)
            # endregion

            for k, val in enumerate(vds):

                # region ----- Process data -----
                x = FET.Sweep.filter_vds_values(fet.data, [val])[:, 0, 0]
                y = FET.Sweep.filter_vds_values(fet.data, [val])[:, 0, 3]
                oxide_thickness = arc[arc["device"] == fet.device]["oxide thickness"].values
                oxide_material = arc[arc["device"] == fet.device]["oxide material"].values
                epsilon_r = mat[mat["material"] == oxide_material]["epsilon_r"].values
                l = arc[arc["device"] == fet.device]["channel length"].values
                w = arc[arc["device"] == fet.device]["channel width"].values
                y_smooth = savgol_filter(y, int(2 * floor(smooth_window * len(x) / 2) + 1), smooth_order)    # smooth Ids
                # endregion

                # region ----- Calculate mobility -----
                if 0 in region:  # linear region
                    plot0.ax0.plot(x, y, **plot0.lookIds, label=f"{chip}-{device}", color=cm(norm(m)))  # plot Ids vs Vgs raw
                    plot0.ax0.plot(x, y_smooth, **plot0.lookSmooth, color="black")  # plot Ids smooth vs Vgs
                    dy_dx = abs(gradient(y, x))  # calculate d(ids)/d(vgs) raw
                    dy_smooth_dx = abs(gradient(y_smooth, x))  # calculate d(ids)/d(vgs)
                    c = epsilon_0 * epsilon_r / oxide_thickness
                    mu_lin = l / (w * c * val) * dy_dx
                    mu_lin_smooth = l / (w * c * val) * dy_smooth_dx
                    plot0.ax1.plot(x, 1e4*mu_lin, **plot0.lookIds, color=cm(norm(m)))            # plot dy/dx raw
                    plot0.ax1.plot(x, 1e4*mu_lin_smooth, **plot0.lookSmooth, color="black")  # plot dy/dx raw

                if 1 in region:  # saturation region
                    plot0.ax0.plot(x, y, **plot0.lookIds)          # plot Ids vs Vgs raw
                    plot0.ax0.plot(x, y_smooth, **plot0.lookSmooth)  # plot Ids smooth vs Vgs
                    sqrty = sqrt(abs(y))                            # calculate sqrt(Ids)
                    sqrty_smooth = sqrt(abs(y_smooth))              # smooth sqrt(Ids)
                    dsqrty_dx = abs(gradient(sqrty, x))                  # calculate d(Ids)/d(Vgs)
                    dsqrty_smooth_dx = abs(gradient(sqrty_smooth, x))    # calculate d(Ids smooth)/d(Vgs)
                    c = epsilon_0 * epsilon_r / oxide_thickness
                    mu_sat = 2 * l / (w * c) * dsqrty_dx
                    mu_sat_smooth = 2 * l / (w * c) * dsqrty_smooth_dx
                    plot0.ax1.plot(x, 1e4 * mu_sat, **plot0.lookIds)                  # plot dy/dx raw
                    plot0.ax1.plot(x, 1e4 * mu_sat_smooth, **plot0.lookSmooth)          # plot dy/dx raw
                # endregion

        m = m + 1

plot0.ax0.legend()
plt.show()
