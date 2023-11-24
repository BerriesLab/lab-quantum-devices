# region ----- Import packages -----
import matplotlib.gridspec
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
import os
import numpy as np
import pickle
import scipy.stats
import datetime
# endregion

main = "C:/Users/dabe/Google Drive/Work/Projects/2019 - QuIET/Experimental/Data"              # Main folder
chip = "TEP16"                        # chip [string]:    chip name
device = "F24"                                # device [string]:  device string
path = main + "/" + chip + "/" + device + "/"
ms = 6  # marker size
t_range = [290, 310]

# region ----- Load bin files in memory -----
print("Loading bin file in memory... ", end="")
os.chdir(path)
files = [x for x in os.listdir() if x.endswith(".bin")]
datas = []
for file in files:
    with open(file, "rb") as f:
        data = pickle.load(f)
        if t_range[0] <= data["data"]["temperature"] <= t_range[1]:
            datas.append(data)
print("Done.")
print("Found {} files.".format(len(datas)))
# endregion

# region ----- Initialize figure -----
print("Initializing figure... ", end="")

# matplotlib.rcParams["font.family"] = "open sans"
matplotlib.rcParams["font.size"] = 10

fig = plt.figure(figsize=(30/2.54, 20/2.54))
grid = matplotlib.gridspec.GridSpec(nrows=6, ncols=3)
grid.update(wspace=0.4, hspace=2)
# -----
axR1T = fig.add_subplot(grid[0:4, 0])
axR1T.set_xlabel("Temperature (K)")
axR1T.set_ylabel(r"$R$ ($\Omega$)")
axR1T.set_title("Thermometer 1", fontsize=10, fontstyle="italic")
# -----
axR1Tres = fig.add_subplot(grid[4:6, 0])
axR1Tres.set_xlabel("Temperature (K)")
axR1Tres.set_ylabel(r"$\Delta$R ($\Omega$)")
# -----
axR2T = fig.add_subplot(grid[0:4, 1])
axR2T.set_xlabel("Temperature (K)")
axR2T.set_ylabel(r"R ($\Omega$)")
axR2T.set_title("Thermometer 2", fontsize=10, fontstyle="italic")
# -----
axR2Tres = fig.add_subplot(grid[4:6, 1])
axR2Tres.set_xlabel("Temperature (K)")
axR2Tres.set_ylabel(r"$\Delta$R ($\Omega$)")
# -----
axdTi = fig.add_subplot(grid[0:2, 2])
axdTi.set_xlabel("Current (mA)")
axdTi.set_ylabel(r"dT (K)")
axdTi.set_title("Oscillation amplitudes", fontsize=10, fontstyle="italic")
# -----
axTavgi = fig.add_subplot(grid[2:4, 2])
axTavgi.set_xlabel("Current (mA)")
axTavgi.set_ylabel(r"$\Delta$T$_{avg}$ (K)")
axTavgi.set_title("Temperature drift", fontsize=10, fontstyle="italic")
# -----
axdTlpfi = fig.add_subplot(grid[4:6, 2])
axdTlpfi.set_xlabel("Current (mA)")
axdTlpfi.set_ylabel(r"$\Delta$T (K)")
axdTlpfi.set_title("Temperature difference", fontsize=10, fontstyle="italic")
# -----
axR1Tres.get_shared_y_axes().join(axR1Tres, axR2Tres)
print("Done.")
# endregion

# region ----- Make arrays -----
t1, r1, t2, r2 = [], [], [], []
cal_rt, cal_ti = False, False  # to track calibration file
for data in datas:
    if data["experiment"] == "calibration r(t)":
        cal_rt = True
        if data["thermometer"] == 1:
            t1.append(data["data"]["temperature"])
            r1.append(data["data"]["resistance"])
        if data["thermometer"] == 2:
            t2.append(data["data"]["temperature"])
            r2.append(data["data"]["resistance"])
    if data["experiment"] == "calibration dr(i)":
        cal_ti = True
        if data["thermometer"] == 1:
            i1 = data["data"]["heater current"]
            t = data["data"]["temperature"]
            dr1x = data["data"]["post-processed"]["dr x"]
            dr1x_std_dev = data["data"]["post-processed"]["dr x std dev"]
            dr1y = data["data"]["post-processed"]["dr y"]
            dr1y_std_dev = data["data"]["post-processed"]["dr y std dev"]
            dr1_lpf = data["data"]["post-processed"]["dr lpf"]
            dr1_lpf_std_err = data["data"]["post-processed"]["dr lpf std err"]
        if data["thermometer"] == 2:
            i2 = data["data"]["heater current"]
            t = data["data"]["temperature"]
            dr2x = data["data"]["post-processed"]["dr x"]
            dr2x_std_dev = data["data"]["post-processed"]["dr x std dev"]
            dr2y = data["data"]["post-processed"]["dr y"]
            dr2y_std_dev = data["data"]["post-processed"]["dr y std dev"]
            dr2_lpf = data["data"]["post-processed"]["dr lpf"]
            dr2_lpf_std_err = data["data"]["post-processed"]["dr lpf std err"]
r1 = np.array(r1)
t1 = np.array(t1)
r2 = np.array(r2)
t2 = np.array(t2)
# endregion

# region ----- Make color map -----
c = matplotlib.cm.get_cmap("RdYlBu_r")
norm = matplotlib.colors.Normalize(vmin=np.min(np.append(t1, t2)), vmax=np.max(np.append(t1, t2)))
# endregion

# region ----- Plot experiment: calibration r(t) -----
if cal_rt is True:
    print("Plotting calibration: R(T)... ", end="")
    axR1T.scatter(t1, r1, marker="o", s=50, color=c(norm(t1)), edgecolor="black", alpha=0.5)
    fit_1 = scipy.stats.linregress(t1, r1)
    a11 = fit_1.slope
    a10 = fit_1.intercept
    a11_stderr = fit_1.stderr
    r1fit = a10 + a11 * t1
    axR1T.plot(t1, r1fit, linewidth=1, linestyle="--", color="red", alpha=0.5)
    axR1Tres.fill_between(t1, r1 - r1fit, 0, facecolor="grey", alpha=0.5)
    axR1Tres.scatter(t1, r1 - r1fit, marker="o", s=50, color=c(norm(t1)), edgecolor="black", alpha=0.5)

    axR2T.scatter(t2, r2, marker="o", s=50, color=c(norm(t2)), edgecolor="black", alpha=0.5)
    fit_2 = scipy.stats.linregress(t2, r2)
    a21 = fit_2.slope
    a20 = fit_2.intercept
    a21_stderr = fit_2.stderr
    r2fit = a20 + a21 * t2
    axR2T.plot(t2, r2fit, linewidth=1, linestyle="--", color="red", alpha=0.5)
    axR2Tres.fill_between(t2, r2 - r2fit, 0, facecolor="grey", alpha=0.5)
    axR2Tres.scatter(t2, r2 - r2fit, marker="o", s=50, color=c(norm(t1)), edgecolor="black", alpha=0.5)
    print("Done.")
# endregion

# region ----- Plot experiment: calibration T(i) -----
if cal_ti is True:
    print("Plotting calibration: T(I)... ", end="")
    dtx = - (dr1x / a11 - dr2x / a21)
    dtx_err = np.sqrt((dr1x_std_dev / a11) ** 2 + (dr1x * a11_stderr / a11 ** 2) ** 2 + (dr2x_std_dev / a21) ** 2 + (dr2x * a21_stderr / a21 ** 2) ** 2)
    axdTi.errorbar(i1*1e3, dtx, yerr=dtx_err, marker="o", ms=ms, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,0$")

    dty = -(dr1y / a11 - dr2y / a21)
    dty_err = np.sqrt((dr1y_std_dev / a11) ** 2 + (dr1y * a11_stderr / a11 ** 2) ** 2 + (dr2y_std_dev / a21) ** 2 + (dr2y * a21_stderr / a21 ** 2) ** 2)
    axdTi.errorbar(i1*1e3, dty, yerr=dty_err, marker="D", ms=ms, linewidth=0, capsize=3, ecolor="black", elinewidth=1, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5, label=r"$2\omega,\pi/2$")
    axdTi.legend()

    tavg = (dr1_lpf / a11 + dr2_lpf / a21) / 2
    tavg_err = np.sqrt((dr1_lpf_std_err / a11) ** 2 + () ** 2)
    axTavgi.plot(i1*1e3, tavg, marker="o", ms=ms, linewidth=0, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)

    dt = (dr1_lpf / a11 - dr2_lpf / a21)
    axdTlpfi.plot(i1*1e3, dt, marker="o", ms=ms, linewidth=0, markerfacecolor=c(norm(t)), markeredgecolor="black", alpha=0.5)
    print("Done.")
# endregion

# region ----- Save figure -----
path = main + "/" + chip + "/" + device + "/processed"
try:
    os.chdir(path)  # if path exists, then make it cwd
    print("{} ... found.".format(path))
except OSError:  # if path does not exists
    print("{} ... not found. Making directory... ".format(path))
    os.makedirs(path)  # make new directory
    os.chdir(path)  # make path cwd
print("Current working directory set to: {}".format(os.getcwd()))
print("Saving figure to {}... ".format(os.getcwd()), end="")
date = datetime.datetime.now().strftime("%Y.%m.%d %H.%M.%S")
plt.savefig(fname="{} - Calibration summary in the range {:04.1f} - {:04.1f} K.png".format(date, np.min(np.append(t1, t2)), np.max(np.append(t1, t2))), format="png")
print("Done.")
# endregion

plt.show()