# region ----- Import packages -----
import matplotlib.gridspec
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
import os
import numpy as np
import pickle
import scipy.stats

# endregion

main = "C:/Users/dabe/Google Drive/Work/Projects/2020 - TeTra/Experimental/Data"  # Main folder
chip = "TeTra00_1.2"  # chip [string]:    chip name
device = "G"  # device [string]:  device string
path = main + "/" + chip + "/" + device + "/"
ms = 7  # marker size
t_range = [290, 310]

# region ----- Load bin files in memory -----
os.chdir(path)
files = [x for x in os.listdir() if x.endswith(".bin")]
datas = []
for file in files:
    with open(file, "rb") as f:
        data = pickle.load(f)
        if t_range[0] <= data["data"]["temperature"] <= t_range[1]:
            datas.append(data)
# endregion

# region ----- Initialize Figure 1: experiment summary -----
print("Initializing Figure 1: experiment summary... ", end="")
fig = plt.figure(figsize=(30 / 2.54, 20 / 2.54))
grid = matplotlib.gridspec.GridSpec(nrows=6, ncols=3)
grid.update(wspace=0.4, hspace=2)

axiv1 = fig.add_subplot(grid[0:3, 0])
axiv1.set_xlabel("$I_{th}$ ($\mu$A)")
axiv1.set_ylabel("V (mV)")
axiv1.set_title("Thermometer 1 iv(s)", fontsize=10, fontstyle="italic")
# -----
axiv2 = fig.add_subplot(grid[3:6, 0])
axiv2.set_xlabel("$I_{th}$ ($\mu$A)")
axiv2.set_ylabel("V (mV)")
axiv2.set_title("Thermometer 2 iv(s)", fontsize=10, fontstyle="italic")
# -----
axRT = fig.add_subplot(grid[0:4, 1])
axRT.set_xlabel("T (K)")
axRT.set_ylabel(r"$R$ ($\Omega$)")
axRT.set_title("R(T)", fontsize=10, fontstyle="italic")
# -----
axRerrT = fig.add_subplot(grid[4:6, 1])
axRerrT.set_xlabel("T (K)")
axRerrT.set_ylabel("Std. err. (m$\Omega$)")
# -----
axdRxi = fig.add_subplot(grid[0:2, 2])
axdRxi.set_xlabel("$I_h$ (mA)")
axdRxi.set_ylabel(r"$dR_{2\omega_1,0}$ (m$\Omega$)")
axdRxi.set_title("x-oscillation amplitudes", fontsize=10, fontstyle="italic")
# -----
axdRyi = fig.add_subplot(grid[2:4, 2])
axdRyi.set_xlabel("$I_h$ (mA)")
axdRyi.set_ylabel(r"$dR_{2\omega_1,\frac{\pi}{2}}$ (m$\Omega$)")
axdRyi.set_title("y-oscillation amplitudes", fontsize=10, fontstyle="italic")
# -----
axdRlpfi = fig.add_subplot(grid[4:5, 2])
axdRlpfi.set_xlabel("Current (mA)")
axdRlpfi.set_ylabel(r"$dR_{2\omega_1,LPF}$ (m$\Omega$)")
axdRlpfi.set_title("Drift", fontsize=10, fontstyle="italic")
# -----
axdRlpferri = fig.add_subplot(grid[5:6, 2])
axdRlpferri.set_xlabel("Current (mA)")
axdRlpferri.set_ylabel("Std. err. (m$\Omega$)")
axdRlpferri.set_title("Drift std. err.", fontsize=10, fontstyle="italic")
# -----
axdRxi.get_shared_y_axes().join(axdRxi, axdRyi)
print("Done.")
# endregion

# region ----- Make color map -----
t_min = np.infty
t_max = 0
for data in datas:
    if data["data"]["temperature"] < t_min:
        t_min = data["data"]["temperature"]
    if data["data"]["temperature"] > t_max:
        t_max = data["data"]["temperature"]
c = matplotlib.cm.get_cmap("RdYlBu_r")
norm = matplotlib.colors.Normalize(vmin=t_min, vmax=t_max)
# endregion

# region ----- Plot -----
for data in datas:

    # region ----- Experiment summary: r(t) -----
    if data["experiment"] == "calibration r(t)":
        i = data["data"]["iv"][:, 0]
        v = data["data"]["iv"][:, 1]
        t = data["data"]["temperature"]
        r = data["data"]["resistance"]
        r_std_err = data["data"]["standard error"]
        if data["thermometer"] == 1:
            axiv1.plot(i * 1e6, v * 1e3, marker="o", ms=ms, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axRT.plot(t, r, marker="o", ms=ms, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axRerrT.plot(t, r_std_err * 1e3, marker="o", ms=ms, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
        if data["thermometer"] == 2:
            axiv2.plot(i * 1e6, v * 1e3, marker="D", ms=ms, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axRT.plot(t, r, marker="D", ms=ms, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axRerrT.plot(t, r_std_err * 1e3, marker="D", ms=ms, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
    # endregion

    # region ----- Experiment summary: dr(i) -----
    if data["experiment"] == "calibration dr(i)":
        i = data["data"]["heater current"]
        t = data["data"]["temperature"]
        drx = data["data"]["post-processed"]["dr x"]
        drx_std_dev = data["data"]["post-processed"]["dr x std dev"]
        dry = data["data"]["post-processed"]["dr y"]
        dry_std_dev = data["data"]["post-processed"]["dr y std dev"]
        dr_lpf = data["data"]["post-processed"]["dr lpf"]
        dr_lpf_std_err = data["data"]["post-processed"]["dr lpf std err"]
        if data["thermometer"] == 1:
            axdRxi.plot(i * 1e3, drx * 1e3, marker="o", ms=ms, linewidth=0, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axdRyi.plot(i * 1e3, dry * 1e3, marker="o", ms=ms, linewidth=0, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axdRlpfi.plot(i * 1e3, dr_lpf * 1e3, marker="o", ms=ms, linewidth=0, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axdRlpferri.plot(i * 1e3, dr_lpf_std_err * 1e3, marker="D", ms=ms, linewidth=0, color="black", markerfacecolor=c(norm(t)), markeredgecolor="black",
                             alpha=0.5)
        if data["thermometer"] == 2:
            axdRxi.plot(i * 1e3, drx * 1e3, marker="D", ms=ms, linewidth=0, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axdRyi.plot(i * 1e3, dry * 1e3, marker="D", ms=ms, linewidth=0, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axdRlpfi.plot(i * 1e3, dr_lpf * 1e3, marker="D", ms=ms, linewidth=0, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
            axdRlpferri.plot(i * 1e3, dr_lpf_std_err * 1e3, marker="D", ms=ms, linewidth=0, color="black", markerfacecolor=c(norm(t)), markeredgecolor="black",
                             alpha=0.5)
    # endregion
plt.show()