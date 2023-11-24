# region ----- Import packages -----
import matplotlib.gridspec
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.lines
#from Thermoelectrics.Data_analysis.functions import *
from Objects.measurement import *
from scipy.optimize import curve_fit
import numpy as np
from numpy import savetxt
import pickle
# endregion

main = r"C:/Data"
chip = "tep_ch5_00"
device = "c3"
# arrange filenames as [(th1, th2, [h1_th1, h1_th2], [h2_th1, h2_th1]), ...]
calibration = [("2022-05-11 21.25.02 - tep_ch5_00 - c3 - calibration", "2022-05-13 10.28.35 - tep_ch5_00 - c3 - calibration",
                ["2022-05-11 21.25.02 - tep_ch5_00 - c3 - calibration", "2022-05-13 10.28.35 - tep_ch5_00 - c3 - calibration"], [None, None])]
               # ("2021-11-22 17.38.24", "2021-11-23 11.52.15", ["2021-11-22 17.38.24", "2021-11-23 11.52.15"], [None, None]),
               # ("2021-11-25 14.43.32", "2021-11-28 18.19.01", ["2021-11-25 14.43.32", "2021-11-28 18.19.01"], [None, None])]
tmin, tmax = 99, 309

# region ----- Load bin files in memory -----
files = []
for idx, experiment in enumerate(calibration):
    try:
        filename_th1 = rf"{main}\{chip}\{device}\calibration\{experiment[0]}.data"
        print(f"Loading experiment {filename_th1}... ", end="")
        with open(filename_th1, "rb") as f:
            file_th1 = pickle.load(f)
            print("Done.")
        if not (isinstance(file_th1, Experiment) and isinstance(file_th1.data, Thermoelectrics.Calibration)):
            exit("The passed object is not Calibration type.")

        filename_th2 = rf"{main}\{chip}\{device}\calibration\{experiment[1]}.data"
        print(f"Loading experiment {filename_th2}... ", end="")
        with open(filename_th2, "rb") as f:
            file_th2 = pickle.load(f)
            print("Done.")
        if not (isinstance(file_th2, Experiment) and isinstance(file_th2.data, Thermoelectrics.Calibration)):
            exit("The passed object is not Calibration type.")

    except FileNotFoundError:
        exit("Cannot find thermometer calibration files... Program terminates.")

    try:
        filename_h1_th1 = rf"{main}\{chip}\{device}\calibration\{experiment[2][0]}.data"
        print(f"Loading experiment {filename_h1_th1}... ", end="")
        with open(filename_h1_th1, "rb") as f:
            file_h1_th1 = pickle.load(f)
            print("Done.")
        if not(isinstance(file_h1_th1, Experiment) and isinstance(file_h1_th1.data, Thermoelectrics.Calibration)):
            exit("The passed object is not Calibration type.")

        filename_h1_th2 = rf"{main}\{chip}\{device}\calibration\{experiment[2][1]}.data"
        print(f"Loading experiment {filename_h1_th2}... ", end="")
        with open(filename_h1_th2, "rb") as f:
            file_h1_th2 = pickle.load(f)
            print("Done.")
        if not(isinstance(file_h1_th2, Experiment) and isinstance(file_h1_th2.data, Thermoelectrics.Calibration)):
            exit("The passed object is not Calibration type.")

    except FileNotFoundError:
        print("Cannot find heater 1 calibration files...")

    try:
        filename_h2_th1 = rf"{main}\{chip}\{device}\calibration\{experiment[3][0]}.data"
        print(f"Loading experiment {filename_h2_th1}... ", end="")
        with open(filename_h2_th1, "rb") as f:
            file_h2_th1 = pickle.load(f)
        if not(isinstance(file_h2_th1, Experiment) and isinstance(file_h2_th1.data, Thermoelectrics.Calibration)):
            exit("The passed object is not Calibration type.")

        filename_h2_th2 = rf"{main}\{chip}\{device}\calibration\{experiment[3][1]}.data"
        print(f"Loading experiment {filename_h2_th2}... ", end="")
        with open(filename_h2_th2, "rb") as f:
            file_h2_th2 = pickle.load(f)
        if not(isinstance(file_h2_th2, Experiment) and isinstance(file_h2_th2.data, Thermoelectrics.Calibration)):
            exit("The passed object is not Calibration type.")
        flag_h2 = True

    except FileNotFoundError:
        file_h2_th1 = None
        file_h2_th2 = None
        print("Cannot find heater 2 calibration files...")

    files.append((file_th1, file_th2, [file_h1_th1, file_h1_th2], [file_h2_th1, file_h2_th2]))
# endregion

# region ----- Initialize figure -----
print("Initializing figure... ", end="")

# matplotlib.rcParams["font.family"] = "open sans"
matplotlib.rcParams["font.size"] = 10
c = matplotlib.cm.get_cmap("RdYlBu_r")
norm = matplotlib.colors.Normalize(vmin=tmin, vmax=tmax)

fig = plt.figure(figsize=(30/2.54, 25/2.54))
grid = matplotlib.gridspec.GridSpec(nrows=6, ncols=3)
grid.update(top=0.95, bottom=0.11, left=0.08, right=0.96, hspace=1.5, wspace=0.3)
# -----
axr1t = fig.add_subplot(grid[0:4, 0])
axr1t.set_xlabel("$T - T_H$")
axr1t.set_ylabel(r"$R/R_H$")
axr1t.set_title("Thermometer 1", fontsize=10, fontstyle="italic")
# -----
axr1t_err = fig.add_subplot(grid[4:6, 0])
axr1t_err.set_xlabel("$T - T_H$")
axr1t_err.set_ylabel(r"$\Delta R/R_H$ (%)")
# -----
axr2t = fig.add_subplot(grid[0:4, 1])
axr2t.set_xlabel("$T - T_H$")
axr2t.set_ylabel(r"$R/R_H$")
axr2t.set_title("Thermometer 2", fontsize=10, fontstyle="italic")
# -----
axr2t_err = fig.add_subplot(grid[4:6, 1])
axr2t_err.set_xlabel("$T - T_H$")
axr2t_err.set_ylabel(r"$\Delta R/R_H$ (%)")
# -----
axdti = fig.add_subplot(grid[0:2, 2])
axdti.set_xlabel("Current (mA)")
axdti.set_ylabel(r"$\Delta T_{2\omega_{\alpha}}$ (K)")
axdti.set_title("Oscillation amplitudes", fontsize=10, fontstyle="italic")
# -----
axdtdci = fig.add_subplot(grid[2:4, 2])
axdtdci.set_xlabel("Current (mA)")
axdtdci.set_ylabel(r"$\Delta T_{DC}$ (K)")
axdtdci.set_title("Temperature difference", fontsize=10, fontstyle="italic")
# -----
axdtdcavgi = fig.add_subplot(grid[4:6, 2])
axdtdcavgi.set_xlabel("Current (mA)")
axdtdcavgi.set_ylabel(r"$\Delta T_{avg}$ (K)")
axdtdcavgi.set_title("Temperature drift", fontsize=10, fontstyle="italic")
# -----
# fig1 = plt.figure(figsize=(30/2.54, 20/2.54))
# fig1.suptitle("Thermometer 1")
# grid1 = matplotlib.gridspec.GridSpec(nrows=6, ncols=2)
# grid1.update(top=0.9, bottom=0.11, left=0.08, right=0.96, hspace=1, wspace=0.2)
# axdtx1 = fig1.add_subplot(grid1[0:4, 0])
# axdtx1.set_xlabel("Current (mA)")
# axdtx1.set_ylabel(r"$T_{2\omega,0}$ (K)")
# axdtx1.set_title("x-component", fontsize=10, fontstyle="italic")
# axdtx1_err = fig1.add_subplot(grid1[4:6, 0])
# axdtx1_err.set_xlabel("Current (mA)")
# axdtx1_err.set_ylabel(r"$\Delta T_{2\omega,0}$ (K)")
# axdty1 = fig1.add_subplot(grid1[0:4, 1], sharey=axdtx1)
# axdty1.set_xlabel("Current (mA)")
# axdty1.set_ylabel(r"$T_{2\omega,\pi/2}$ (K)")
# axdty1.set_title("y-component", fontsize=10, fontstyle="italic")
# axdty1_err = fig1.add_subplot(grid1[4:6, 1], sharey=axdtx1_err)
# axdty1_err.set_xlabel("Current (mA)")
# axdty1_err.set_ylabel(r"$\Delta T_{2\omega,\pi/2}$ (K)")
# # -----
# fig2 = plt.figure(figsize=(30/2.54, 20/2.54))
# fig2.suptitle("Thermometer 2")
# grid2 = matplotlib.gridspec.GridSpec(nrows=6, ncols=2)
# grid2.update(top=0.9, bottom=0.11, left=0.08, right=0.96, hspace=1, wspace=0.2)
# axdtx2 = fig2.add_subplot(grid2[0:4, 0])
# axdtx2.set_xlabel("Current (mA)")
# axdtx2.set_ylabel(r"$T_{2\omega,0}$ (K)")
# axdtx2.set_title("x-component", fontsize=10, fontstyle="italic")
# axdtx2_err = fig2.add_subplot(grid2[4:6, 0])
# axdtx2_err.set_xlabel("Current (mA)")
# axdtx2_err.set_ylabel(r"$\Delta T_{2\omega,0}$ (K)")
# axdty2 = fig2.add_subplot(grid2[0:4, 1], sharey=axdtx2)
# axdty2.set_xlabel("Current (mA)")
# axdty2.set_ylabel(r"$T_{2\omega,\pi/2}$ (K)")
# axdty2.set_title("y-component", fontsize=10, fontstyle="italic")
# axdty2_err = fig2.add_subplot(grid2[4:6, 1], sharey=axdtx2_err)
# axdty2_err.set_xlabel("Current (mA)")
# axdty2_err.set_ylabel(r"$\Delta T_{2\omega,\pi/2}$ (K)")
print("Done.")
# endregion

# region ----- Build plots -----
names1, names2 = [], []
lines1, lines2 = [], []
for idx, experiment in enumerate(files):

    t1, r1, r1_err, fit1 = Thermoelectrics.Calibration.get_resistance(experiment[0].data, 1)
    t2, r2, r2_err, fit2 = Thermoelectrics.Calibration.get_resistance(experiment[1].data, 2)
    if experiment[2][0] is not None and experiment[2][1] is not None:
        t_h1th1, i_h1th1, drdc11, drdc_err11, drx11, drx_err11, dry11, dry_err11 = Thermoelectrics.Calibration.get_heater_sweep(experiment[2][0].data, 1, 1)
        t_h1th2, i_h1th2, drdc12, drdc_err12, drx12, drx_err12, dry12, dry_err12 = Thermoelectrics.Calibration.get_heater_sweep(experiment[2][1].data, 1, 2)
        if t_h1th1 != t_h1th2 or all(i_h1th1 != i_h1th2):
            exit("Temperature mismatch between heater calibration on thermometer 1 and thermometer 2")
    if experiment[3][0] is not None and experiment[3][1] is not None:
        t_h2th1, i_h2th1, drdc21, drdc_err21, drx21, drx_err21, dry21, dry_err21 = Thermoelectrics.Calibration.get_heater_sweep(experiment[3][0].data, 2, 1)
        t_h2th2, i_h2th2, drdc22, drdc_err22, drx22, drx_err22, dry22, dry_err22 = Thermoelectrics.Calibration.get_heater_sweep(experiment[3][1].data, 2, 2)
        if t_h2th1 != t_h2th2 or all(i_h2th1 != i_h2th2):
            exit("Temperature mismatch between heater calibration on thermometer 1 and thermometer 2")

    t_rescale = t_h1th1

    # plot
    axr1t.scatter(t1 - t_rescale, r1/r1[t1 == t_rescale], marker="o", s=50, color=c(norm(t1)), edgecolor="black", alpha=0.5)
    axr1t.plot(t1 - t_rescale, (fit1[1] + fit1[0] * t1)/r1[t1 == t_rescale], linewidth=1, linestyle="--", color="red", alpha=0.5)
    axr1t_err.fill_between(t1 - t_rescale, 100*(r1 - (fit1[1] + fit1[0] * t1))/r1[t1 == t_rescale], 0, facecolor="grey", alpha=0.5)
    axr1t_err.scatter(t1 - t_rescale, 100*(r1 - (fit1[1] + fit1[0] * t1))/r1[t1 == t_rescale], marker="o", s=50, color=c(norm(t1)), edgecolor="black", alpha=0.5)
    axr1t_err.set_ylim([-100*(r1.max()-r1.min())/r1[t1 == t_rescale]/len(r1), +100*(r1.max()-r1.min())/r1[t1 == t_rescale]/len(r1)])
    lines1.append(matplotlib.lines.Line2D([], [], color=c(norm(t_rescale)), marker='o', linestyle='None', markersize=7, markeredgecolor="black", alpha=0.5))
    names1.append(f"$a_1({int(t_rescale):3d}\ K)$ = {1e3*fit1[0]:.1f} $\pm$ {1e3*fit1[4]:.1f} m$\Omega$/K")

    axr2t.scatter(t2 - t_rescale, r2/r2[t2 == t_rescale], marker="o", s=50, color=c(norm(t2)), edgecolor="black", alpha=0.5)
    axr2t.plot(t2 - t_rescale, (fit2[1] + fit2[0] * t2)/r2[t2 == t_rescale], linewidth=1, linestyle="--", color="red", alpha=0.5)
    axr2t_err.fill_between(t2 - t_rescale, 100*(r2 - (fit2[1] + fit2[0] * t2))/r2[t2 == t_rescale], 0, facecolor="grey", alpha=0.5)
    axr2t_err.scatter(t2 - t_rescale, 100*(r2 - (fit2[1] + fit2[0] * t2))/r2[t2 == t_rescale], marker="o", s=50, color=c(norm(t2)), edgecolor="black", alpha=0.5)
    axr2t_err.set_ylim([-100*(r2.max()-r2.min())/r2[t2 == t_rescale]/len(r2), +100*(r2.max()-r2.min())/r2[t2 == t_rescale]/len(r2)])
    lines2.append(matplotlib.lines.Line2D([], [], color=c(norm(t_rescale)), marker='o', linestyle='None', markersize=7, markeredgecolor="black", alpha=0.5))
    names2.append(f"$a_1({int(t_rescale):3d}\ K)$ = {1e3*fit2[0]:.1f} $\pm$ {1e3*fit2[4]:.1f} m$\Omega$/K")

    if experiment[2][0] is not None and experiment[2][1] is not None:

        t, i, drdc11, drdc_err11, drx11, drx_err11, dry11, dry_err11 = Thermoelectrics.Calibration.get_heater_sweep(experiment[2][0].data, 1, 1)
        dtdc11, dtdc_err11, dtx11, dtx_err11, dty11, dty_err11 = Thermoelectrics.Calibration.calculate_temperatures(drdc11, drdc_err11, drx11, drx_err11, dry11, dry_err11, fit1)
        # axdtx1.scatter(i*1e3, dtx11, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdtx1_err.fill_between(i*1e3, dtx_err11, 0, facecolor="grey", alpha=0.5)
        # axdtx1_err.scatter(i*1e3, dtx_err11, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdty1.scatter(i*1e3, dty11, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdty1_err.fill_between(i*1e3, dty_err11, 0, facecolor="grey", alpha=0.5)
        # axdty1_err.scatter(i*1e3, dty_err11, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        axdtdcavgi.errorbar(x=i*1e3, y=dtdc11, yerr=dtdc_err11, marker="o", ms=7, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")

        t, i, drdc12, drdc_err12, drx12, drx_err12, dry12, dry_err12 = Thermoelectrics.Calibration.get_heater_sweep(experiment[2][1].data, 1, 2)
        dtdc12, dtdc_err12, dtx12, dtx_err12, dty12, dty_err12 = Thermoelectrics.Calibration.calculate_temperatures(drdc12, drdc_err12, drx12, drx_err12, dry12, dry_err12, fit2)
        # axdtx2.scatter(i*1e3, dtx12, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdtx2_err.fill_between(i*1e3, dtx_err12, 0, facecolor="grey", alpha=0.5)
        # axdtx2_err.scatter(i*1e3, dtx_err12, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdty2.scatter(i*1e3, dty12, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdty2_err.fill_between(i*1e3, dty_err12, 0, facecolor="grey", alpha=0.5)
        # axdty2_err.scatter(i*1e3, dty_err12, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        axdtdcavgi.errorbar(x=i*1e3, y=dtdc12, yerr=dtdc_err12, marker="o", ms=7, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")

        dtx1 = dtx11 - dtx12
        dtx_err1 = sqrt(dtx_err11 ** 2 + dtx_err12 ** 2)
        dty1 = dty11 - dty12
        dty_err1 = sqrt(dty_err11 ** 2 + dty_err12 ** 2)
        axdti.errorbar(x=i*1e3, y=dtx1, yerr=dtx_err1, marker="o", markersize=7, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")
        axdti.errorbar(x=i*1e3, y=dty1, yerr=dty_err1, marker="D", markersize=7, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")
        fit1 = curve_fit(lambda x, A: A*x**2, i, dtx1)[0]
        fit2 = curve_fit(lambda x, A: A*x**2, i, dty1)[0]
        axdti.plot(i*1e3, fit1[0]*i**2, linewidth=1, linestyle="--", color="red", alpha=0.5)
        axdti.plot(i*1e3, fit2[0]*i**2, linewidth=1, linestyle="--", color="red", alpha=0.5)
        x_component = matplotlib.lines.Line2D([], [], color=c(norm(t)), marker='o', linestyle='None', markersize=7, label='Blue stars')
        y_component = matplotlib.lines.Line2D([], [], color=c(norm(t)), marker='D', linestyle='None', markersize=7, label='Red squares')
        axdti.legend([x_component, y_component], ["x-component", "y-component"])

        dtdc1 = dtdc11 - dtdc12
        dtdc_err1 = sqrt(dtdc_err11 ** 2 + dtdc_err12 ** 2)
        axdtdci.errorbar(x=i*1e3, y=dtdc1, yerr=dtdc_err1, marker="o", markersize=7, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")
        fitdc1 = curve_fit(lambda x, A: A*x**2, i, dtdc1)[0]
        axdtdci.plot(i*1e3, fitdc1[0]*i**2, linewidth=1, linestyle="--", color="red", alpha=0.5)

        dtavg = (dtdc11 + dtdc12) / 2
        dtavg_err = 1 / 2 * sqrt(dtdc_err11 ** 2 + dtdc_err12 ** 2)
        axdtdcavgi.fill_between(i*1e3, dtdc11, dtdc12, facecolor="grey", alpha=0.5)

    if experiment[3][0] is not None and experiment[3][1] is not None:

        t, i, drdc21, drdc_err21, drx21, drx_err21, dry21, dry_err21 = Thermoelectrics.Calibration.get_heater_sweep(experiment[3][0].data, 2, 1)
        dtdc21, dtdc_err21, dtx21, dtx_err21, dty21, dty_err21 = Thermoelectrics.Calibration.calculate_temperatures(drdc21, drdc_err21, drx21, drx_err21, dry21, dry_err21, fit1)
        # axdtx1.scatter(i*1e3, dtx21, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdtx1_err.fill_between(i, dtx_err21, 0, facecolor="grey", alpha=0.5)
        # axdtx1_err.scatter(i*1e3, dtx_err21, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdty1.scatter(i*1e3, dty21, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdty1_err.fill_between(i*1e3, dty_err21, 0, facecolor="grey", alpha=0.5)
        # axdty1_err.scatter(i*1e3, dty_err21, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        axdtdcavgi.errorbar(x=i*1e3, y=dtdc12, yerr=dtdc_err12, marker="o", ms=8, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")

        t, i, drdc22, drdc_err22, drx22, drx_err22, dry22, dry_err22 = Thermoelectrics.Calibration.get_heater_sweep(experiment[3][1].data, 2, 2)
        dtdc22, dtdc_err22, dtx22, dtx_err22, dty22, dty_err22 = Thermoelectrics.Calibration.calculate_temperatures(drdc22, drdc_err22, drx22, drx_err22, dry22, dry_err22, fit2)
        # axdtx2.scatter(i*1e3, dtx22, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdtx2_err.fill_between(i*1e3, dtx_err22, 0, facecolor="grey", alpha=0.5)
        # axdtx2_err.scatter(i*1e3, dtx_err22, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdty2.scatter(i*1e3, dty22, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        # axdty2_err.fill_between(i*1e3, dty_err22, 0, facecolor="grey", alpha=0.5)
        # axdty2_err.scatter(i*1e3, dty_err22, marker="o", s=50, color=c(norm(t)), edgecolor="black", alpha=0.5)
        axdtdcavgi.errorbar(x=i*1e3, y=dtdc22, yerr=dtdc_err22, marker="o", ms=8, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")

        dtx2 = dtx21 - dtx22
        dtx_err2 = sqrt(dtx21 ** 2 + dtx22 ** 2)
        dty2 = dty21 - dty22
        dty_err2 = sqrt(dty21 ** 2 + dty22 ** 2)
        axdti.errorbar(x=i*1e3, y=dtx2, yerr=dtx_err2, marker="o", s=50, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")
        axdti.errorbar(x=i*1e3, y=dty2, yerr=dty_err2, marker="o", s=50, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")

        dtdc2 = dtdc21 - dtdc22
        dtdc_err2 = sqrt(dtdc_err21 ** 2 + dtdc_err22 ** 2)
        axdtdci.errorbar(x=i*1e3, y=dtdc2, yerr=dtdc_err2, marker="o", s=50, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")

        dtavg = (dtdc21 + dtdc22) / 2
        dtavg_err = sqrt((dtdc_err21 / 2) ** 2 + (dtdc_err22 / 2) ** 2)
        axdtdcavgi.fill_between(i*1e3, dtdc21, dtdc22, facecolor="grey", alpha=0.5)

    if idx == 0:
        x = np.c_[t*np.ones(len(i)), i, dtx1, dtx_err1, dty1, dty_err1, dtdc1, dtdc_err1, dtavg, dtavg_err]
    else:
        xtemp = np.c_[t*np.ones(len(i)), i, dtx1, dtx_err1, dty1, dty_err1, dtdc1, dtdc_err1, dtavg, dtavg_err]
        x = np.concatenate((x, xtemp))

# endregion

axr1t.legend(lines1, names1, prop={"size": 8})
axr2t.legend(lines2, names2, prop={"size": 8})

savetxt(rf"{main}\{chip}\{device}\calibration\calibration.csv", X=x, delimiter=",", header="tbath,i,dtx,dtxerr,dty,dtyerr,dtdc,dtdcerr,dtavg,dtavgerr", comments="")

plt.show()
