import os
from numpy import max, pi, min, inf
import matplotlib.pyplot as plt
import pickle
import itertools
from Utilities.signal_processing import *
from Objects.measurement import FET, Figure
import pandas as pd
import matplotlib.cm
import matplotlib.colors
import matplotlib
from matplotlib.lines import Line2D

"""
#######################################################################
    Author:         Davide Beretta
    Date:           25.10.2022
    Description:    IV plotter
#######################################################################
"""

main = r"D:\My Drive\Work\Projects\2020 - TeTra\Experimental\Electrical data"
# data2load is a list of tuples, where the 1st element is the chip name, the 2nd is the device list
data2load = [("qd_gr03", ["ed", "ee", "ef", "eg", "ej", "ek",]),
             ("qd_gr04", ["df", "dg", "dh",
                          ])]
cycle_vds = 2           # [int] i-th Vds cycle where to calculate mobility
sweep_vds = 2           # [int] direction of the Vds sweep where to extract the mobility: {0: all, 1: fwd, 2: bkw}
region = [0]            # [list of int] region where to extract mobility: linear (0), saturation (1)
smooth_window = 20/100  # [float] windon to smooth (in % of array lenght)
smooth_order = 3        # [int] order of the polynomial used to smooth
filter_measurment_environment = [0]  # {0: vacuum}
filter_thickness = [-inf,  inf]
scaling_v = [-1, -0.5, 0.5, 1]
d = 1e-6 * array([5, 10, 15, 20, 25, 30, 50])
area = pi * (d / 2) ** 2
thick_map = {"qd_gr03": {"dc": 150e-9, "dd": 100e-9, "de": 100e-9, "df": 100e-9, "dg": 150e-9, "dh":150e-9, "di": 500e-9, "dj": 300e-9, "dk": 200e-9,
                         "ec": 500e-9, "ed": 220e-9, "ee": 370e-9, "ef": 530e-9, "eg": 240e-9, "eh": 100e-9, "ei": 1200e-9, "ej": 330e-9, "ek":150e-9},
             "qd_gr04": {"dc": 75e-9, "dd": 75e-9, "de": 400e-9, "df": 190e-9, "dg": 90e-9, "dh":90e-9, "di": 150e-9, "dj": 150e-9, "dk": 100e-9,
                         "ec": 700e-9, "ed": 700e-9, "ee": 75e-9, "ef": 150e-9, "eg": 200e-9, "eh": 200e-9, "ei": 150e-9, "ej": 250e-9, "ek":450e-9}}
device_dic = {'a': 5, 'b': 5, 'c': 5, 'd': 10, 'e': 10, 'f': 15, 'g': 15, 'h': 20, 'i': 20, 'j': 20, 'k': 25, 'l': 25,
              'm': 30, 'n': 30, 'o': 50, 'p': 50, 'q': 50}

# region ----- Figures -----
n = sum([len(x[1]) for x in data2load])
cm = matplotlib.cm.get_cmap("RdYlBu_r")
tvalues = list(itertools.chain(*[list(x.values()) for x in thick_map.values()]))
norm_t = matplotlib.colors.LogNorm(max([min(tvalues), filter_thickness[0]]), min([max(tvalues), filter_thickness[1]]))
norm_d = matplotlib.colors.Normalize(0, n)  # norm device
norm_a = matplotlib.colors.LogNorm(min(area), max(area))  # norm area
linestyle = {"linewidth": 1.6, "marker": "o", "markersize": 0, "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 1}
sizex, sizey = 9.5/2.54, 7/2.54
xmin, xmax = -1, 1
plot_iv_a = Figure.PlotLineLinAndLog(title=r"$I$ vs $V$ vs Area", xlabel="$V$ (V)", ylabel="$I$ (A)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_a, cmap_label="Area ($m^2$)", xlim=(xmin, xmax))
plot_iv_t = Figure.PlotLineLinAndLog(title=r"$I$ vs $V$ vs Thickness", xlabel="$V$ (V)", ylabel="$I$ (A)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_t, cmap_label="$L_{CH}$ ($m$)", xlim=(xmin, xmax))
plot_jv_a = Figure.PlotLineLinAndLog(title=r"$J$ vs $V$ vs Area", xlabel="$V$ (V)", ylabel="$J$ ($A/m^2$)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_a, cmap_label="Area ($m^2$)", xlim=(xmin, xmax))
plot_jv_t = Figure.PlotLineLinAndLog(title=r"$J$ vs $V$ vs Thickness", xlabel="$V$ (V)", ylabel="$J$ ($A/m^2$)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_t, cmap_label="$L_{CH}$ ($m$)", xlim=(xmin, xmax))
plot_rr_a = Figure.PlotLineLinAndLog(title=r"$RR$ vs Area", xlabel="$V$ (V)", ylabel="$RR$", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_a, cmap_label="Area ($m^2$)", xlim=(0, xmax))
plot_rr_t = Figure.PlotLineLinAndLog(title=r"$RR$ vs Thickness", xlabel="$V$ (V)", ylabel="$RR$", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_t, cmap_label="$L_{CH}$ ($m$)", xlim=(0, xmax))
plot_iv_n = Figure.PlotLineLinAndLog(title=r"$I \times L_{CH}$ vs $V$ vs Thickness", xlabel="$V$ (V)", ylabel=r"$I \times L_{CH}$ (A $\times$ m)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_t, cmap_label="$L_{CH}$ ($m$)", xlim=(xmin, xmax))
df = pd.DataFrame(data=None, columns=["chip", "device", "diameter", "area", "thickness", "voltage", "current"], index=None)
# endregion

m = 0
for chip_devices in data2load:  # run over the (chip, [devices]) tuples to load

    chip = chip_devices[0]
    devices = chip_devices[1]

    for device in devices:  # run over the devices to load

        if not filter_thickness[0] < thick_map[chip][device] < filter_thickness[1]:
            continue 
        experiments = os.listdir(rf"{main}\{chip}\{device}\iv")
        experiments = [x for x in experiments if x.endswith(".data")]

        val_d = 1e-6 * device_dic[device[0]]
        area = pi*(val_d/2)**2
        thickness = thick_map[chip][device]
        if val_d in d:

            for experiment in experiments:  # run over the experiments to load

                # region ----- Load files -----
                path = rf"{main}\{chip}\{device}\iv\{experiment}"
                with open(path, "rb") as file:
                    fet = pickle.load(file)
                if fet.data.environment not in filter_measurment_environment:
                    continue
                # endregion

                print(rf"Processing {chip} - {device} - {thickness} - {experiment}... ", end="")

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
                y_density = y / (pi*(val_d/2)**2)
                rr = zeros_like(x[x>=0])
                for idx, val in enumerate(x[x>=0]):
                    rr[idx] = y_density[x == val] / y_density[x == -val]
                df=df.append({"chip": chip,
                              "device": device,
                              "diameter": val_d,
                              "area": area,
                              "thickness": thickness,
                              "voltage": [x],
                              "current": [y]}, ignore_index=True)
                print("Done.")  # endregion

                # # region ----- Plot -----
                plot_iv_a.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y, **linestyle, label=f"{chip}-{device}", color=plot_iv_a.fig_lin.cmap(norm_a(area))))
                plot_iv_a.fig_lin.ax.relim()
                plot_iv_a.fig_lin.ax.autoscale_view()
                plot_iv_a.fig_lin.fig.canvas.draw()
                plot_iv_a.fig_lin.fig.tight_layout()
                plot_iv_a.fig_lin.fig.savefig(f"{main}\iv_a_lin.png")
                plot_iv_a.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y), **linestyle, label=f"{chip}-{device}", color=plot_iv_a.fig_log.cmap(norm_a(area))))
                plot_iv_a.fig_log.ax.relim()
                plot_iv_a.fig_log.ax.autoscale_view()
                plot_iv_a.fig_log.fig.canvas.draw()
                plot_iv_a.fig_log.fig.tight_layout()
                plot_iv_a.fig_log.fig.savefig(f"{main}\iv_a_log.png")
                # #
                plot_iv_t.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y, **linestyle, label=f"{chip}-{device}", color=plot_iv_t.fig_lin.cmap(norm_t(thickness))))
                plot_iv_t.fig_lin.ax.relim()
                plot_iv_t.fig_lin.ax.autoscale_view()
                plot_iv_t.fig_lin.fig.canvas.draw()
                plot_iv_t.fig_lin.fig.tight_layout()
                plot_iv_t.fig_lin.fig.savefig(f"{main}\iv_t_lin.png")
                plot_iv_t.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y), **linestyle, label=f"{chip}-{device}", color=plot_iv_t.fig_log.cmap(norm_t(thickness))))
                plot_iv_t.fig_log.ax.relim()
                plot_iv_t.fig_log.ax.autoscale_view()
                plot_iv_t.fig_log.fig.canvas.draw()
                plot_iv_t.fig_log.fig.tight_layout()
                plot_iv_t.fig_log.fig.savefig(f"{main}\iv_t_log.png")
                #
                plot_jv_a.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y_density, **linestyle, label=f"{chip}-{device}", color=plot_jv_a.fig_lin.cmap(norm_a(area))))
                plot_jv_a.fig_lin.ax.relim()
                plot_jv_a.fig_lin.ax.autoscale_view()
                plot_jv_a.fig_lin.fig.canvas.draw()
                plot_jv_a.fig_lin.fig.tight_layout()
                plot_jv_a.fig_lin.fig.savefig(f"{main}\jv_a_lin.png")
                plot_jv_a.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y_density), **linestyle, label=f"{chip}-{device}", color=plot_jv_a.fig_log.cmap(norm_a(area))))
                plot_jv_a.fig_log.ax.relim()
                plot_jv_a.fig_log.ax.autoscale_view()
                plot_jv_a.fig_log.fig.canvas.draw()
                plot_jv_a.fig_log.fig.tight_layout()
                plot_jv_a.fig_log.fig.savefig(f"{main}\jv_a_log.png")

                plot_jv_t.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y_density, **linestyle, label=f"{chip}-{device}", color=plot_jv_t.fig_lin.cmap(norm_t(thickness))))
                plot_jv_t.fig_lin.ax.relim()
                plot_jv_t.fig_lin.ax.autoscale_view()
                plot_jv_t.fig_lin.fig.canvas.draw()
                plot_jv_t.fig_lin.fig.tight_layout()
                plot_jv_t.fig_lin.fig.savefig(f"{main}\jv_t_lin.png")
                plot_jv_t.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y_density), **linestyle, label=f"{chip}-{device}", color=plot_jv_t.fig_log.cmap(norm_t(thickness))))
                plot_jv_t.fig_log.ax.relim()
                plot_jv_t.fig_log.ax.autoscale_view()
                plot_jv_t.fig_log.fig.canvas.draw()
                plot_jv_t.fig_log.fig.tight_layout()
                plot_jv_t.fig_log.fig.savefig(f"{main}\jv_t_log.png")

                plot_rr_a.fig_lin.ax.add_line(Line2D(xdata=x[x>=0], ydata=rr, **linestyle, label=f"{chip}-{device}", color=plot_rr_a.fig_lin.cmap(norm_a(area))))
                plot_rr_a.fig_lin.ax.relim()
                plot_rr_a.fig_lin.ax.autoscale_view()
                plot_rr_a.fig_lin.fig.canvas.draw()
                plot_rr_a.fig_lin.fig.tight_layout()
                plot_rr_a.fig_lin.fig.savefig(rf"{main}\rr_a_lin.png")
                plot_rr_a.fig_log.ax.add_line(Line2D(xdata=x[x>=0], ydata=abs(rr), **linestyle, label=f"{chip}-{device}", color=plot_rr_a.fig_log.cmap(norm_a(area))))
                plot_rr_a.fig_log.ax.relim()
                plot_rr_a.fig_log.ax.autoscale_view()
                plot_rr_a.fig_log.fig.canvas.draw()
                plot_rr_a.fig_log.fig.tight_layout()
                plot_rr_a.fig_log.fig.savefig(rf"{main}\rr_a_log.png")

                plot_rr_t.fig_lin.ax.add_line(Line2D(xdata=x[x>=0], ydata=rr, **linestyle, label=f"{chip}-{device}", color=plot_rr_a.fig_lin.cmap(norm_t(thickness))))
                plot_rr_t.fig_lin.ax.relim()
                plot_rr_t.fig_lin.ax.autoscale_view()
                plot_rr_t.fig_lin.fig.canvas.draw()
                plot_rr_t.fig_lin.fig.tight_layout()
                plot_rr_t.fig_lin.fig.savefig(rf"{main}\rr_t_lin.png")
                plot_rr_t.fig_log.ax.add_line(Line2D(xdata=x[x>=0], ydata=abs(rr), **linestyle, label=f"{chip}-{device}", color=plot_rr_a.fig_log.cmap(norm_t(thickness))))
                plot_rr_t.fig_log.ax.relim()
                plot_rr_t.fig_log.ax.autoscale_view()
                plot_rr_t.fig_log.fig.canvas.draw()
                plot_rr_t.fig_log.fig.tight_layout()
                plot_rr_t.fig_log.fig.savefig(rf"{main}\rr_t_log.png")

                plot_iv_n.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y * thickness, **linestyle, label=f"{chip}-{device}", color=plot_iv_n.fig_lin.cmap(norm_t(thickness))))
                plot_iv_n.fig_lin.ax.relim()
                plot_iv_n.fig_lin.ax.autoscale_view()
                plot_iv_n.fig_lin.fig.canvas.draw()
                plot_iv_n.fig_lin.fig.tight_layout()
                plot_iv_n.fig_lin.fig.savefig(rf"{main}\iv_n_lin.png")
                plot_iv_n.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y * thickness), **linestyle, label=f"{chip}-{device}", color=plot_iv_n.fig_log.cmap(norm_t(thickness))))
                plot_iv_n.fig_log.ax.relim()
                plot_iv_n.fig_log.ax.autoscale_view()
                plot_iv_n.fig_log.fig.canvas.draw()
                plot_iv_n.fig_log.fig.tight_layout()
                plot_iv_n.fig_log.fig.savefig(rf"{main}\iv_n_log.png")

                m = m+1
                #endregion

df.to_pickle(f"{main}\data.pkl")
df.to_csv(f"{main}\data.csv")
plt.show()
