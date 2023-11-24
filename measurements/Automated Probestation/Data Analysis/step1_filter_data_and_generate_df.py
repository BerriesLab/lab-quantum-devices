import os
from numpy import gradient, floor, loadtxt, argwhere, sqrt, r_, count_nonzero
from scipy.stats import linregress
from matplotlib.lines import Line2D
import matplotlib.colors
import pandas as pd
from scipy.constants import epsilon_0
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import Utilities.signal_processing
from Objects.measurement import Figure
import datetime


main = r"C:\Data\automated probestation\osja_gfet04_gr_p5"
chips = [x for x in os.listdir(main) if os.path.isdir(rf"{main}\{x}")]
overwrite = True
architecture = "gfet06"
l_dict = {"P01": 100e-6, "P02": 50e-6, "P03": 20e-6, "P04": 10e-6, "P05": 5e-6, "P06": 2e-6, "P07": 1e-6}
mat_dict = {"gr": "gr",
            "gr_c60": "gr/c60",
            "pristine": "gr",
            "pristine_longvac": "gr_longvac",
            "c60": "gr/c60",
            "gr_p3ht": "gr/p3ht",
            "gr_p5": "gr/p5",
            "pentacene_d1": "gr/p5 d1",
            "pentacene_d2": "gr/p5 d2",
            "pentacene_d5": "gr/p5 d5"}
w = 5e-6
bias = 50e-3
sweep_dir = 1  # "bkw"
smooth_window = 20/100  # [float] windon to smooth (in % of array lenght)
smooth_order = 3        # [int] order of the polynomial used to smooth
epsilon_r = 3.9
oxide_thickness = 285e-9  # 330e-9

filter_rvalue = 0.99        # [float] min. value of IV linear fit r-value to accept the fit
filter_stderr = 100         # [float] normal distribution test of IV residuals
filter_rmin = 1e2           # [float] min. resistance (from IV) to accept the curve
filter_rmax = 1e6           # [float] max. resistance (from IV) to accept the curve
filter_ids_min = 1e-9       # [float] min. I_DS current in V_GS sweep below which the curve is discarded
filter_gradient = 0.01      # [float] percentage (between 0-1) of max current

def r_tot_tlm(L, W, R_s, R_c):
    return R_s * L / W + 2 * R_c / W

def r_tot_fit(mu, n, L, W, R_c):
    return R_c + L / W / mu / n

def n(n0, C, V_GS, V_D):
    return sqrt(n0 ** 2 + C * (V_GS - V_D))

def capacitance(e0, er, t):
    return e0 * er / t

cm = matplotlib.cm.get_cmap("coolwarm")
norm = matplotlib.colors.LogNorm(1e-6, 100e-6)
normbar = matplotlib.colors.LogNorm(1e-6, 100e-6)
sizex = 9.5/2.54
sizey = 7/2.54
cmap_label = "$L_{CH}$ (m)"
linestyle = {"markersize": 0, "linewidth": 1, "alpha": 0.6}
matplotlib.rcParams.update({'font.size': 8})
plotiv = Figure.PlotLine("$V_{DS}$ (V)", "$I_{DS}$ (A)", title=r"$I_{DS}$ vs $V_{DS}$", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotiv.fig.tight_layout()
plotiv_log = Figure.PlotLine("$V_{DS}$ (V)", "$I_{DS}$ (A)", semilogy=True, title=r"$I_{DS}$ vs $V_{DS}$", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotiv_log.fig.tight_layout()
plotiv_kill = Figure.PlotLine("$V_{DS}$ (V)", "$I_{DS}$ (A)", title=r"$I_{DS}$ vs $V_{DS}$ killed", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotiv_kill.fig.tight_layout()
plotiv_kill_log = Figure.PlotLine("$V_{DS}$ (V)", "$I_{DS}$ (A)", title=r"$I_{DS}$ vs $V_{DS}$", semilogy=True, sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotiv_kill_log.fig.tight_layout()
plotiv_norm = Figure.PlotLine(r"$V_{DS}$ (V)", "$I_{DS} \\times L_{CH}$ (A m)", title=r"$I_{DS} \times L_{CH}$ vs $V_{DS}$", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotiv_norm.fig.tight_layout()
plotgs = Figure.PlotLine("$V_{GS}$ (V)", "$I_{DS}$ (A)", title=r"$I_{DS}$ vs $V_{GS}$", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotgs.fig.tight_layout()
plotgs_log = Figure.PlotLine("$V_{GS}$ (V)", "$I_{DS}$ (A)", semilogy=True, title=r"$I_{DS}$ vs $V_{GS}$", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotgs_log.fig.tight_layout()
plotgs_kill = Figure.PlotLine("$V_{GS}$ (V)", "$I_{DS}$ (A)", title=r"$I_{DS}$ vs $V_{GS}$ killed", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotgs_kill.fig.tight_layout()
plotgs_kill_log = Figure.PlotLine("$V_{GS}$ (V)", "$I_{DS}$ (A)", title=r"$I_{DS}$ vs $V_{GS}$ killed", semilogy=True, sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotgs_kill_log.fig.tight_layout()
plotgs_norm = Figure.PlotLine(r"$V_{GS}$ (V)", "$I_{DS} \\times L_{CH}$ (A m)", title=r"$I_{DS} \times L_{CH}$ vs $V_{GS}$", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotgs_norm.fig.tight_layout()
plotmu = Figure.PlotLine("$V_{GS}$ (V)", "$\mu$ ($m^2V^{-1}s^{-1}$)", title=r"$\sim dI_{DS}/dV_{GS}$", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotmu.fig.tight_layout()
plotd2y = Figure.PlotLine("$V_{GS}$ (V)", "$d^{2}I_{DS}$", title=r"$d^{2}I_{DS}/dV_{GS}^{2}$", sizex=sizex, sizey=sizey, cmap=cm, norm=normbar, cmap_label=cmap_label)
plotd2y.fig.tight_layout()
plt.show(block=False)
plt.pause(0.25)

if overwrite is True:
    df = pd.DataFrame(data=None, columns=["chip", "device", "w", "l", "material", "vgs", "ids"])
elif overwrite is False:
    try:
        df = pd.read_pickle(f"{main}\data.pkl")
    except:
        df = pd.DataFrame(data=None, columns=["chip", "device", "w", "l", "material", "vgs", "ids"])
else:
    exit("Overwrite wrong value.")

counter = 0
tot = 0
for chip in chips:

    devices = os.listdir(rf"{main}\{chip}\IV_Data")
    devices = [x[7:] for x in devices if x.endswith(".dat")]
    n = len(devices)
    date = datetime.datetime.strptime([x for x in os.listdir(rf"{main}\{chip}") if x.endswith("Info.txt")][0][-28:-18], "%Y_%m_%d")
    # print(date)

    for idx, device in enumerate(devices):
        tot += 1

        print(f"{chip}-{device} - Loading IV... ", end="")
        with open(rf"{main}\{chip}\IV_Data\IVData_{device}", "r") as file:
            data_iv = loadtxt(file, skiprows=77)
            l = l_dict[device[8:-4]]

        if sweep_dir == 0:
            data_iv = Utilities.signal_processing.filter_fwd_sweep(data_iv)
        if sweep_dir == 1:
            data_iv = Utilities.signal_processing.filter_bkw_sweep(data_iv)
        fit = linregress(data_iv[:, 1], data_iv[:, 0])
        if not(fit[2] > filter_rvalue and filter_rmax > fit[0] > filter_rmin and fit[4] < filter_stderr):
            print(f"Discarded.")
            plotiv_kill.ax.add_line(Line2D(xdata=data_iv[:, 0], ydata=data_iv[:, 1], color=cm(norm(l)), **linestyle))
            plotiv_kill.ax.relim()
            plotiv_kill.ax.autoscale_view()
            plotiv_kill.fig.canvas.draw()
            plotiv_kill_log.ax.add_line(Line2D(xdata=data_iv[:, 0], ydata=abs(data_iv[:, 1]), color=cm(norm(l)), **linestyle))
            plotiv_kill_log.ax.relim()
            plotiv_kill_log.ax.autoscale_view()
            plotiv_kill_log.fig.canvas.draw()
            plt.pause(0.1)
            counter += 1
            continue
        else:
            print("OK... ", end="")
            plotiv.ax.add_line(Line2D(xdata=data_iv[:, 0], ydata=data_iv[:, 1], color=cm(norm(l)), **linestyle))
            plotiv.ax.relim()
            plotiv.ax.autoscale_view()
            plotiv.fig.canvas.draw()
            plotiv_log.ax.add_line(Line2D(xdata=data_iv[:, 0], ydata=abs(data_iv[:, 1]), color=cm(norm(l)), **linestyle))
            plotiv_log.ax.relim()
            plotiv_log.ax.autoscale_view()
            plotiv_log.fig.canvas.draw()
            plotiv_norm.ax.add_line(Line2D(xdata=data_iv[:, 0], ydata=data_iv[:, 1] * l, color=cm(norm(l)), **linestyle))
            plotiv_norm.ax.relim()
            plotiv_norm.ax.autoscale_view()
            plotiv_norm.fig.canvas.draw()
            plt.pause(0.1)


        print(f"Loading Gate Sweep... ", end="")
        with open(rf"{main}\{chip}\GateSweep_Data\GateSweepData_{device}", "r") as file:
            data_vgs = loadtxt(file, skiprows=77)
        if sweep_dir == 0:
            data_vgs = Utilities.signal_processing.filter_fwd_sweep(data_vgs)
        if sweep_dir == 1:
            data_vgs = Utilities.signal_processing.filter_bkw_sweep(data_vgs)
        y_smooth = savgol_filter(data_vgs[:, 1], int(2 * floor(smooth_window * len(data_vgs[:, 0]) / 2) + 1), smooth_order)
        y2_smooth = gradient(y_smooth[:])
        plotd2y.ax.add_line(Line2D(xdata=data_vgs[:, 0], ydata=y2_smooth, color=cm(norm(l)), **linestyle))
        plotd2y.ax.relim()
        plotd2y.ax.autoscale_view()
        plotd2y.fig.canvas.draw()
        if any(data_vgs[:, 1] < filter_ids_min) \
                or any(abs(gradient(data_vgs[:, 1])) > filter_gradient * abs(data_vgs[:, 1])) \
                or all(i < j for i, j in zip(y_smooth[:], y_smooth[1:]))\
                or count_nonzero(r_[True, y_smooth[1:] < y_smooth[:-1]][1:-1] & r_[y_smooth[:-1] < y_smooth[1:], True][1:-1]) > 1:
            print(f"Discarded.")
            plotgs_kill.ax.add_line(Line2D(xdata=data_vgs[:, 0], ydata=data_vgs[:, 1], color=cm(norm(l)), **linestyle))
            plotgs_kill.ax.relim()
            plotgs_kill.ax.autoscale_view()
            plotgs_kill.fig.canvas.draw()
            plotgs_kill_log.ax.add_line(Line2D(xdata=data_vgs[:, 0], ydata=abs(data_vgs[:, 1]), color=cm(norm(l)), **linestyle))
            plotgs_kill_log.ax.relim()
            plotgs_kill_log.ax.autoscale_view()
            plotgs_kill_log.fig.canvas.draw()
            plt.pause(0.1)
            counter += 1
            continue
        else:
            print("OK... ", end="")
            plotgs.ax.add_line(Line2D(xdata=data_vgs[:, 0], ydata=data_vgs[:, 1], color=cm(norm(l)), **linestyle))
            plotgs.ax.relim()
            plotgs.ax.autoscale_view()
            plotgs.fig.canvas.draw()
            plotgs_log.ax.add_line(Line2D(xdata=data_vgs[:, 0], ydata=abs(data_vgs[:, 1]), color=cm(norm(l)), **linestyle))
            plotgs_log.ax.relim()
            plotgs_log.ax.autoscale_view()
            plotgs_log.fig.canvas.draw()
            plotgs_norm.ax.add_line(Line2D(xdata=data_vgs[:, 0], ydata=data_vgs[:, 1] * l, color=cm(norm(l)), **linestyle))
            plotgs_norm.ax.relim()
            plotgs_norm.ax.autoscale_view()
            plotgs_norm.fig.canvas.draw()
            plt.pause(0.1)


        print(f"Calculate mobility... ", end="")
        dy_dx = abs(gradient(data_vgs[:, 1], data_vgs[:, 0]))   # calculate d(ids)/d(vgs) raw
        v_dirac = data_vgs[argwhere(dy_dx == min(dy_dx)), 0][0]
        y_smooth = savgol_filter(data_vgs[:, 1], int(2 * floor(smooth_window * len(data_vgs[:, 0]) / 2) + 1), smooth_order)
        dy_smooth_dx = abs(gradient(y_smooth, data_vgs[:, 0]))   # calculate d(ids)/d(vgs)
        c = capacitance(epsilon_0, epsilon_r, oxide_thickness)
        mu_lin = l / (w * c * bias) * dy_dx
        mu_lin_smooth = l / (w * c * bias) * dy_smooth_dx
        plotmu.ax.add_line(Line2D(xdata=data_vgs[:, 0], ydata=mu_lin_smooth, color=cm(norm(l)), **linestyle))
        plotmu.ax.relim()
        plotmu.ax.autoscale_view()
        plotmu.fig.canvas.draw()
        plt.pause(0.1)
        try:
            mu_h = max(mu_lin_smooth[argwhere(data_vgs[:, 0] <= v_dirac[0])])[0]
        except:
            mu_h = None
        try:
            mu_e = max(mu_lin_smooth[argwhere(data_vgs[:, 0] >= v_dirac[0])])[0]
        except:
            mu_e = None
        material = mat_dict[chip[12:-5]]
        chip_name = chip[:11]
        if int(chip[-1]) != int(device[5:7]):
            device_name = f"{device[0:5]}{int(chip[-1]):02d}{device[-8:-4]}"
        else:
            device_name = device[:-4]


        print(f"Update DataFrame... ", end="")
        df_temp = pd.DataFrame(data=None, columns=["chip", "device", "w", "l", "material", "vgs", "ids", "date"])
        df_temp["vgs"] = data_vgs[:, 0]
        df_temp["ids"] = data_vgs[:, 1]
        df_temp["chip"] = chip_name
        df_temp["device"] = device_name
        df_temp["w"] = w
        df_temp["l"] = l
        df_temp["material"] = material
        df_temp["date"] = pd.to_datetime(date)
        df = df.append(df_temp)
        print("Done.")
        # print(df_temp)


print(f"OK/TOTAL: {tot-counter}/{tot}")
print(df)
df.to_pickle(f"{main}\data.pkl")
plotiv.fig.tight_layout()
plotiv.fig.savefig(f"{main}\iv.tiff")
plotiv_log.fig.tight_layout()
plotiv_log.fig.savefig(f"{main}\iv log.tiff")
plotiv_norm.fig.tight_layout()
plotiv_norm.fig.savefig(f"{main}\iv norm.tiff")
plotiv_kill.fig.tight_layout()
plotiv_kill.fig.savefig(f"{main}\iv kill.tiff")
plotiv_kill_log.fig.tight_layout()
plotiv_kill_log.fig.savefig(f"{main}\iv kill log.tiff")
plotgs.fig.tight_layout()
plotgs.fig.savefig(f"{main}\gs.tiff")
plotgs_log.fig.tight_layout()
plotgs_log.fig.savefig(f"{main}\gs log.tiff")
plotgs_norm.fig.tight_layout()
plotgs_norm.fig.savefig(f"{main}\gs norm.tiff")
plotgs_kill.fig.tight_layout()
plotgs_kill.fig.savefig(f"{main}\gs kill.tiff")
plotgs_kill_log.fig.tight_layout()
plotgs_kill_log.fig.savefig(f"{main}\gs kill log.tiff")
plotmu.fig.tight_layout()
plotmu.fig.savefig(f"{main}\gs mu.tiff")
plotd2y.fig.tight_layout()
plotd2y.fig.savefig(f"{main}\gs d2y_dvgs.tiff")
plt.show()
