# region ----- Import packages -----
import os
from numpy import gradient, floor, where, unique, max, zeros_like, pi, mean, log, exp, log10, where, min, sign, delete
import matplotlib.pyplot as plt
import pickle
from scipy.signal import savgol_filter
from Utilities.signal_processing import *
from Objects.measurement import FET, Figure
import pandas as pd
import matplotlib
from matplotlib.lines import Line2D  # endregion
from figure_functions import *

"""
#######################################################################
    Author:         Davide Beretta
    Date:           07.01.2022
    Description:    IV plotter
#######################################################################
"""

# region ----- User inputs -----
main = r"C:\Samples"                # main directory
devices2load = ["de"]
data2load = [("qd_gr_03", devices2load)]  # list of tuples, where the 1st element is the chip name, the 2nd is the device list
cycle_vds = 2           # [int] i-th Vds cycle where to calculate mobility
sweep_vds = 2           # [int] direction of the Vds sweep where to extract the mobility: {0: all, 1: fwd, 2: bkw}
region = [0]            # [list of int] region where to extract mobility: linear (0), saturation (1)
smooth_window = 20/100  # [float] windon to smooth (in % of array lenght)
smooth_order = 3        # [int] order of the polynomial used to smooth
# filters
measurment_environment = [0]  # {0: vacuum}
# processes
normalize = True
asymmetry = True
scaling_v = [-1, -0.5, 0.5, 1]
d = [5, 10, 15, 20, 25, 30, 50]
# endregion

# generate figures
n = sum([len(x[1]) for x in data2load])
plot0 = Figure.PlotLinAndLog(n=0, title="I-V", xlabel="$V$ (V)", ylabel="$I$ (A)")  # plot IVs
plot1 = Figure.PlotLinAndLog(n=0, title="J-V", xlabel="$V$ (8)", ylabel="$J$ ($\mu A/\mu m^2$)")
plot2 = Figure.PlotLinAndLog(n=0, title="J-V Normalized", xlabel="$V$ (V)", ylabel="$J/|J_{max}|$")  # plot IVs normalized
plot3 = Figure.PlotLinAndLog(n=0, title="J-V Asymmetry", xlabel="$V$ (V)", ylabel="$[I(V) - I(-V)]/I(V)$")  # plot asymmetry
plot4 = Figure.PlotLinAndLog(n=0, title="Areal Scaling", xlabel="$1/Area$ ($\mu m^{-2}$)", ylabel="$R$ ($\Omega$)", logx=True, grid=True)  # plot asymmetry
plot5 = Figure.PlotLinAndLog(n=0, title="Areal Scaling", xlabel="Area ($\mu m^{2}$)", ylabel="$J$ ($A/m^2$)", logx=True, grid=True)  # plot asymmetry
plot6 = Figure.PlotLinAndLog(n=0, title="Transort mechanism - Schottky-like", xlabel="$V$ (V)", ylabel="$J$ ($\mu A/\mu m^2$)", logx=True)
df = pd.DataFrame(data=None, columns=["chi", "device", "diameter", "area", "voltage", "current"], index=None)
cm = matplotlib.cm.get_cmap("RdYlBu_r")
norm = matplotlib.colors.Normalize(5, 50)
count = 0
for x in data2load:
    devices = os.listdir(rf"{main}\{x[0]}")
    for device in devices:
        if os.path.isdir(rf"{main}\{x[0]}\{device}"):
            experiments = os.listdir(rf"{main}\{x[0]}\{device}\iv")
            experiments = [x for x in experiments if x.endswith(".data")]
            count = count + len(experiments)
norm_device = matplotlib.colors.Normalize(0, count)
device_dic = {'a': 5, 'b': 5, 'c': 5, 'd': 10, 'e': 10, 'f': 15, 'g': 15, 'h': 20, 'i': 20, 'j': 20, 'k': 25, 'l': 25,
              'm': 30, 'n': 30, 'o': 50, 'p': 50, 'q': 50}
color_dic = {5: cm(norm(0)), 10: cm(norm(1)), 15: cm(norm(2)), 20: cm(norm(3)), 25: cm(norm(4)), 30: cm(norm(5)), 50: cm(norm(6))}
marker_dic = {5: 'o', 10: 'o', 15: 'o', 20: 'o', 25: 'o', 30: 'o', 50: 'o'}
m = 0

for chip_devices in data2load:  # run over the (chip, [devices]) tuples to load

    chip = chip_devices[0]
    devices = chip_devices[1]

    for device in devices:  # run over the devices to load

        experiments = os.listdir(rf"{main}\{chip}\{device}\iv")

        val_d = device_dic[device[0]]
        if val_d in d:

            for experiment in experiments:  # run over the experiments to load

                # region ----- Load files -----
                path = rf"{main}\{chip}\{device}\iv\{experiment}"
                with open(path, "rb") as file:
                    fet = pickle.load(file)
                if fet.data.environment not in measurment_environment:
                    continue
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
                x = fet.data.data[0, :, 2]
                y = fet.data.data[0, :, 3]
                # x = fet.data.data[:, :, 2]
                # y = fet.data.data[:, :, 3]
                y_density = y * 1e6 / (pi*(val_d/2)**2)
                ynorm = where(y>=0, y_density / max(y_density), -y_density / min(y_density))
                y_v = flip(ynorm)
                yasym = (ynorm + y_v) / ynorm
                for idx, val_v in enumerate(scaling_v):
                    row = {"chip": chip, "device": device, "diameter": val_d, "area": pi*(val_d*1e-6/2)**2,
                           "voltage": x[x==val_v][0], "current": y[x==val_v][0], "resistance": x[x==val_v][0]/y[x==val_v][0]}
                    df=df.append(row, ignore_index=True)
                # endregion

                # plot
                # plot0.ax0.add_line(Line2D(xdata=[None], ydata=[None], **plot0.lookIds, label=f"{val_d} $\mu$m"))
                # plot0.ax1.add_line(Line2D(xdata=[None], ydata=[None], **plot0.lookIds, label=f"{val_d} $\mu$m"))
                plot0.ax0.add_line(Line2D(xdata=[None], ydata=[None], **plot0.lookIds, label=f"{device}"))
                plot0.ax1.add_line(Line2D(xdata=[None], ydata=[None], **plot0.lookIds, label=f"{device}"))
                plot0.ax0.lines[m].set_data(x, y)
                plot0.ax0.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot0.ax0.lines[m].set_color(cm(norm_device(m)))
                plot0.ax1.lines[m].set_data(x, abs(y))
                plot0.ax1.lines[m].set_color(cm(norm_device(m)))
                plot0.ax0.relim()
                plot0.ax0.autoscale_view(["x", "y"])
                plot0.ax1.relim()
                plot0.ax1.autoscale_view(["x", "y"])

                plot1.ax0.add_line(Line2D(xdata=[None], ydata=[None], **plot1.lookIds, label=f"{val_d} $\mu$m"))
                plot1.ax1.add_line(Line2D(xdata=[None], ydata=[None], **plot1.lookIds, label=f"{val_d} $\mu$m"))
                plot1.ax0.lines[m].set_data(x, y_density)
                plot1.ax0.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot1.ax1.lines[m].set_data(x, abs(y_density))
                plot1.ax1.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot1.ax0.relim()
                plot1.ax0.autoscale_view(["x", "y"])
                plot1.ax1.relim()
                plot1.ax1.autoscale_view(["x", "y"])

                plot2.ax0.add_line(Line2D(xdata=[None], ydata=[None], **plot2.lookIds, label=f"{val_d} $\mu$m"))
                plot2.ax1.add_line(Line2D(xdata=[None], ydata=[None], **plot2.lookIds, label=f"{val_d} $\mu$m"))
                plot2.ax0.lines[m].set_data(x, ynorm)
                plot2.ax0.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot2.ax1.lines[m].set_data(x, abs(ynorm))
                plot2.ax1.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot2.ax0.relim()
                plot2.ax0.autoscale_view(["x", "y"])
                plot2.ax1.relim()
                plot2.ax1.autoscale_view(["x", "y"])

                plot3.ax0.add_line(Line2D(xdata=[None], ydata=[None], **plot3.lookIds, label=f"{val_d} $\mu$m"))
                plot3.ax1.add_line(Line2D(xdata=[None], ydata=[None], **plot3.lookIds, label=f"{val_d} $\mu$m"))
                plot3.ax0.lines[m].set_data(x, yasym)
                plot3.ax0.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot3.ax1.lines[m].set_data(x, abs(yasym))
                plot3.ax1.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot3.ax0.relim()
                plot3.ax0.autoscale_view(["x", "y"])
                plot3.ax1.relim()
                plot3.ax1.autoscale_view(["x", "y"])

                plot6.ax0.add_line(Line2D(xdata=[None], ydata=[None], **plot6.lookIds, label=f"{val_d} $\mu$m"))
                plot6.ax1.add_line(Line2D(xdata=[None], ydata=[None], **plot6.lookIds, label=f"{val_d} $\mu$m"))
                plot6.ax0.lines[m].set_data(abs(x), y_density)
                plot6.ax0.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot6.ax1.lines[m].set_data(abs(x), abs(y_density))
                plot6.ax1.lines[m].set_color(cm(norm(device_dic[device[0]])))
                plot6.ax0.relim()
                plot6.ax0.autoscale_view(["x", "y"])
                plot6.ax1.relim()
                plot6.ax1.autoscale_view(["x", "y"])

                m = m+1

# Generates unique labels
legend_without_duplicate_labels(plot0.ax0)
legend_without_duplicate_labels(plot1.ax0)
legend_without_duplicate_labels(plot2.ax0)
legend_without_duplicate_labels(plot3.ax0)

norm = matplotlib.colors.Normalize(min(scaling_v), max(scaling_v))
custom_handles, custom_labels = [], []
for idx_v, val_v in enumerate(scaling_v):
    plot2.ax0.axvline(val_v, 0, 1, linewidth=1, linestyle="-.", alpha=0.2, color="black")
    plot2.ax1.axvline(val_v, 0, 1, linewidth=1, linestyle="-.", alpha=0.2, color="black")
    x = zeros_like(df["area"].unique())
    y = zeros_like(x)
    ymax = zeros_like(x)
    ymin = zeros_like(x)
    yj = zeros_like(x)
    yjmax = zeros_like(x)
    yjmin = zeros_like(x)
    for idx_a, val_a in enumerate(df["area"].unique()):
        temp = df[(df["voltage"]==val_v) & (df["area"]==val_a)]
        x[idx_a] = 1/(val_a*1e12)
        y[idx_a] = temp["resistance"].mean()
        ymax[idx_a] = temp["resistance"].max()
        ymin[idx_a] = temp["resistance"].min()
        yj[idx_a] = (temp["current"]/temp["area"]).mean()
        yjmax[idx_a] = (temp["current"]/temp["area"]).max()
        yjmin[idx_a] = (temp["current"]/temp["area"]).min()
    plot4.ax0.errorbar(x, y, yerr=[ymin, ymax], capsize=5, linestyle="--", linewidth=1, color=cm(norm(val_v)), alpha=0.5, label=f"{val_v:.2f} V")
    plot4.ax0.plot(x, y, linewidth=0, marker="o", markeredgewidth=1, markeredgecolor="black", color=cm(norm(val_v)), alpha=0.5, label=f"{val_v:.2f} V")
    plot4.ax1.errorbar(x, y, yerr=[ymin, ymax], capsize=5, linestyle="--", linewidth=1, color=cm(norm(val_v)), alpha=0.5, label=f"{val_v:.2f} V")
    plot4.ax1.plot(x, y, linewidth=0, marker="o", markeredgewidth=1, markeredgecolor="black", color=cm(norm(val_v)), alpha=0.5, label=f"{val_v:.2f} V")
    plot5.ax0.errorbar(1/x, yj, yerr=[yjmin, yjmax], capsize=5, linestyle="--", linewidth=1, color=cm(norm(val_v)), alpha=0.5, label=f"{val_v:.2f} V")
    plot5.ax0.plot(1/x, yj, linewidth=0, marker="o", markeredgewidth=1, markeredgecolor="black", color=cm(norm(val_v)), alpha=0.5, label=f"{val_v:.2f} V")
    plot5.ax1.errorbar(1/x, abs(yj), yerr=[yjmin, yjmax], capsize=5, linestyle="--", linewidth=1, color=cm(norm(val_v)), alpha=0.5, label=f"{val_v:.2f} V")
    plot5.ax1.plot(1/x, abs(yj), linewidth=0, marker="o", markeredgewidth=1, markeredgecolor="black", color=cm(norm(val_v)), alpha=0.5, label=f"{val_v:.2f} V")
legend_without_duplicate_labels(plot4.ax0)
# legend_without_duplicate_labels(plot4.ax1)
legend_without_duplicate_labels(plot5.ax0)
# legend_without_duplicate_labels(plot5.ax1)

plot4.ax0.autoscale_view(["x", "y"])
plot4.ax1.relim()
plot4.ax1.autoscale_view(["x", "y"])
plot5.ax0.autoscale_view(["x", "y"])
plot5.ax1.relim()
plot5.ax1.autoscale_view(["x", "y"])

plt.show()
