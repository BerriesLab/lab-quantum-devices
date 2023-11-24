import os
from numpy import max, pi, where, min, inf
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
from figure_functions import *

"""
#######################################################################
    Author:         Davide Beretta
    Date:           07.01.2022
    Description:    IV plotter
#######################################################################
"""

main = r"D:\My Drive\Work\Projects\2020 - TeTra\Experimental\Electrical data"
df = pd.read_pickle(f"{main}\data.pkl")
plot_scaling_a = False
plot_scaling_t = True
plot_j = False
plot_i = True
plot_rr = True
plot_ivnorm = True

# region ----- Figures -----
n = len(df.groupby(["chip", "device"]))
cm = matplotlib.cm.get_cmap("RdYlBu_r")
norm_t = matplotlib.colors.Normalize(df["thickness"].min(), df["thickness"].max())
norm_d = matplotlib.colors.Normalize(0, n)
norm_a = matplotlib.colors.LogNorm(df["area"].min(), df["area"].max())
linestyle = {"linewidth": 1.6, "marker": "o", "markersize": 0, "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 1}
sizex, sizey = 9.5/2.54, 7/2.54
xmin, xmax = -1, 1
if plot_scaling_a is True and plot_i is True:
    plot_iv_a = Figure.PlotLineLinAndLog(title=r"$I$ vs $V$ vs Area", xlabel="$V$ (V)", ylabel="$I$ (A)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_a, cmap_label="Area ($m^2$)", xlim=(xmin, xmax))
if plot_scaling_a is True and plot_j is True:
    plot_jv_a = Figure.PlotLineLinAndLog(title=r"$J$ vs $V$ vs Area", xlabel="$V$ (V)", ylabel="$J$ ($A/m^2$)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_a, cmap_label="Area ($m^2$)", xlim=(xmin, xmax))
if plot_scaling_a is True and plot_rr is True:
    plot_rr_a = Figure.PlotLineLinAndLog(title=r"$RR$ vs Area", xlabel="$V$ (V)", ylabel="$RR$", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_a, cmap_label="Area ($m^2$)", xlim=(0, xmax))
if plot_scaling_t is True and plot_i is True:
    plot_iv_t = Figure.PlotLineLinAndLog(title=r"$I$ vs $V$ vs Thickness", xlabel="$V$ (V)", ylabel="$I$ (A)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_t, cmap_label="$L_{CH}$ ($m$)", xlim=(xmin, xmax))
if plot_scaling_t is True and plot_j is True:
    plot_jv_t = Figure.PlotLineLinAndLog(title=r"$J$ vs $V$ vs Thickness", xlabel="$V$ (V)", ylabel="$J$ ($A/m^2$)", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_t, cmap_label="$L_{CH}$ ($m$)", xlim=(xmin, xmax))
if plot_scaling_t is True and plot_rr is True:
    plot_rr_t = Figure.PlotLineLinAndLog(title=r"$RR$ vs Thickness", xlabel="$V$ (V)", ylabel="$RR$", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_t, cmap_label="$L_{CH}$ ($m$)", xlim=(0, xmax))
if plot_scaling_t is True and plot_ivnorm is True:
    plot_ivnorm_t = Figure.PlotLineLinAndLog(title=r"$I/I_{max}$ vs $V$ vs Thickness", xlabel="$V$ (V)", ylabel="$I/I_{max}$", sizex=sizex, sizey=sizey, cmap=cm, norm=norm_t, cmap_label="$L_{CH}$ ($m$)", xlim=(xmin, xmax))


grps = df.groupby(["chip", "device"])
for key, grp in grps:
    print(key)
    x = grp["voltage"].values[0][0]
    y = grp["current"].values[0][0]
    a = grp["area"].values[0]
    t = grp["thickness"].values[0]
    rr = array([y[x == val] / y[x == -val] for idx, val in enumerate(x[x>=0])])

    if plot_scaling_a is True and plot_i is True:
        plot_iv_a.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_iv_a.fig_lin.cmap(norm_a(a))))
        plot_iv_a.fig_lin.ax.relim()
        plot_iv_a.fig_lin.ax.autoscale_view()
        plot_iv_a.fig_lin.fig.canvas.draw()
        plot_iv_a.fig_lin.fig.tight_layout()
        plot_iv_a.fig_lin.fig.savefig(f"{main}\iv_a_lin.png")
        plot_iv_a.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y), **linestyle, label=f"{key[0]}-{key[1]}", color=plot_iv_a.fig_log.cmap(norm_a(a))))
        plot_iv_a.fig_log.ax.relim()
        plot_iv_a.fig_log.ax.autoscale_view()
        plot_iv_a.fig_log.fig.canvas.draw()
        plot_iv_a.fig_log.fig.tight_layout()
        plot_iv_a.fig_log.fig.savefig(f"{main}\iv_a_log.png")

    if plot_scaling_a is True and plot_j is True:
        plot_jv_a.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y/a, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_jv_a.fig_lin.cmap(norm_a(a))))
        plot_jv_a.fig_lin.ax.relim()
        plot_jv_a.fig_lin.ax.autoscale_view()
        plot_jv_a.fig_lin.fig.canvas.draw()
        plot_jv_a.fig_lin.fig.tight_layout()
        plot_jv_a.fig_lin.fig.savefig(f"{main}\jv_a_lin.png")
        plot_jv_a.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y)/a, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_jv_a.fig_log.cmap(norm_a(a))))
        plot_jv_a.fig_log.ax.relim()
        plot_jv_a.fig_log.ax.autoscale_view()
        plot_jv_a.fig_log.fig.canvas.draw()
        plot_jv_a.fig_log.fig.tight_layout()
        plot_jv_a.fig_log.fig.savefig(f"{main}\jv_a_log.png")

    if plot_scaling_a is True and plot_rr is True:
        plot_rr_a.fig_lin.ax.add_line(Line2D(xdata=x[x>=0], ydata=rr, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_rr_a.fig_lin.cmap(norm_a(a))))
        plot_rr_a.fig_lin.ax.relim()
        plot_rr_a.fig_lin.ax.autoscale_view()
        plot_rr_a.fig_lin.fig.canvas.draw()
        plot_rr_a.fig_lin.fig.tight_layout()
        plot_rr_a.fig_lin.fig.savefig(rf"{main}\rr_a_lin.png")
        plot_rr_a.fig_log.ax.add_line(Line2D(xdata=x[x>=0], ydata=abs(rr), **linestyle, label=f"{key[0]}-{key[1]}", color=plot_rr_a.fig_log.cmap(norm_a(a))))
        plot_rr_a.fig_log.ax.relim()
        plot_rr_a.fig_log.ax.autoscale_view()
        plot_rr_a.fig_log.fig.canvas.draw()
        plot_rr_a.fig_log.fig.tight_layout()
        plot_rr_a.fig_log.fig.savefig(rf"{main}\rr_a_log.png")

    if plot_scaling_t is True and plot_i is True:
        plot_iv_t.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_iv_t.fig_lin.cmap(norm_t(t))))
        plot_iv_t.fig_lin.ax.relim()
        plot_iv_t.fig_lin.ax.autoscale_view()
        plot_iv_t.fig_lin.fig.canvas.draw()
        plot_iv_t.fig_lin.fig.tight_layout()
        plot_iv_t.fig_lin.fig.savefig(f"{main}\iv_t_lin.png")
        plot_iv_t.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y), **linestyle, label=f"{key[0]}-{key[1]}", color=plot_iv_t.fig_log.cmap(norm_t(t))))
        plot_iv_t.fig_log.ax.relim()
        plot_iv_t.fig_log.ax.autoscale_view()
        plot_iv_t.fig_log.fig.canvas.draw()
        plot_iv_t.fig_log.fig.tight_layout()
        plot_iv_t.fig_log.fig.savefig(f"{main}\iv_t_log.png")

    if plot_scaling_t is True and plot_j is True:
        plot_jv_t.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y/a, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_jv_t.fig_lin.cmap(norm_t(t))))
        plot_jv_t.fig_lin.ax.relim()
        plot_jv_t.fig_lin.ax.autoscale_view()
        plot_jv_t.fig_lin.fig.canvas.draw()
        plot_jv_t.fig_lin.fig.tight_layout()
        plot_jv_t.fig_lin.fig.savefig(f"{main}\jv_t_lin.png")
        plot_jv_t.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y)/a, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_jv_t.fig_log.cmap(norm_t(t))))
        plot_jv_t.fig_log.ax.relim()
        plot_jv_t.fig_log.ax.autoscale_view()
        plot_jv_t.fig_log.fig.canvas.draw()
        plot_jv_t.fig_log.fig.tight_layout()
        plot_jv_t.fig_log.fig.savefig(f"{main}\jv_t_log.png")

    if plot_scaling_t is True and plot_rr is True:
        plot_rr_t.fig_lin.ax.add_line(Line2D(xdata=x[x>=0], ydata=rr, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_rr_t.fig_lin.cmap(norm_t(t))))
        plot_rr_t.fig_lin.ax.relim()
        plot_rr_t.fig_lin.ax.autoscale_view()
        plot_rr_t.fig_lin.fig.canvas.draw()
        plot_rr_t.fig_lin.fig.tight_layout()
        plot_rr_t.fig_lin.fig.savefig(rf"{main}\rr_t_lin.png")
        plot_rr_t.fig_log.ax.add_line(Line2D(xdata=x[x>=0], ydata=abs(rr), **linestyle, label=f"{key[0]}-{key[1]}", color=plot_rr_t.fig_log.cmap(norm_t(t))))
        plot_rr_t.fig_log.ax.relim()
        plot_rr_t.fig_log.ax.autoscale_view()
        plot_rr_t.fig_log.fig.canvas.draw()
        plot_rr_t.fig_log.fig.tight_layout()
        plot_rr_t.fig_log.fig.savefig(rf"{main}\rr_t_log.png")

    if plot_scaling_t is True and plot_ivnorm is True:
        y_norm = append(y[y>=0] / max(y[y>=0]), -y[y<0] / min(y[y<0]))
        plot_ivnorm_t.fig_lin.ax.add_line(Line2D(xdata=x, ydata=y_norm, **linestyle, label=f"{key[0]}-{key[1]}", color=plot_ivnorm_t.fig_lin.cmap(norm_t(t))))
        plot_ivnorm_t.fig_lin.ax.relim()
        plot_ivnorm_t.fig_lin.ax.autoscale_view()
        plot_ivnorm_t.fig_lin.fig.canvas.draw()
        plot_ivnorm_t.fig_lin.fig.tight_layout()
        plot_ivnorm_t.fig_lin.fig.savefig(f"{main}\ivnorm_t_lin.png")
        plot_ivnorm_t.fig_log.ax.add_line(Line2D(xdata=x, ydata=abs(y_norm), **linestyle, label=f"{key[0]}-{key[1]}", color=plot_ivnorm_t.fig_log.cmap(norm_t(t))))
        plot_ivnorm_t.fig_log.ax.relim()
        plot_ivnorm_t.fig_log.ax.autoscale_view()
        plot_ivnorm_t.fig_log.fig.canvas.draw()
        plot_ivnorm_t.fig_log.fig.tight_layout()
        plot_ivnorm_t.fig_log.fig.savefig(f"{main}\ivnorm_t_log.png")

plt.legend()
plt.show()
