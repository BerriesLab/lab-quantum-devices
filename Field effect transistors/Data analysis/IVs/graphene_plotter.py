import pickle
import os
from Objects.measurement import FET
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
import matplotlib.cm
from matplotlib.lines import Line2D
import pandas as pd

# style
VERY_SMALL_SIZE = 4
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

matplotlib.rc('font', size=SMALL_SIZE)      # controls default text sizes
matplotlib.rc('axes', titlesize=SMALL_SIZE)      # fontsize of the axes title
matplotlib.rc('axes', labelsize=SMALL_SIZE)      # fontsize of the x and y labels
matplotlib.rc('xtick', labelsize=SMALL_SIZE)     # fontsize of the tick labels
matplotlib.rc('ytick', labelsize=SMALL_SIZE)     # fontsize of the tick labels
matplotlib.rc('legend', fontsize=SMALL_SIZE)     # legend fontsize
matplotlib.rc('figure', titlesize=BIGGER_SIZE)   # fontsize of the figure title


main = r"T:"
devices2load = ["ak", "bk",
                "dj", "ej", "ek",
                "fj", "gk",
                "ik",
                "ok"]
data2load = [("qd_gr_00", devices2load)]  # list of tuples, where the 1st element is the chip name, the 2nd is the device list
confidence_band = False
temperature = False
cycle_vds = 0           # [int] i-th Vds cycle where to calculate mobility
sweep_vds = 2           # [int] direction of the Vds sweep where to extract the mobility: {0: all, 1: fwd, 2: bkw}

cm = matplotlib.cm.get_cmap("Pastel2")
norm = Normalize(vmin=0, vmax=6)

device_dic = {'a': 5, 'b': 5, 'c': 5, 'd': 10, 'e': 10, 'f': 15, 'g': 15, 'h': 20, 'i': 20, 'j': 20, 'k': 25, 'l': 25,
              'm': 30, 'n': 30, 'o': 50, 'p': 50, 'q': 50}
color_dic = {5: cm(norm(0)), 10: cm(norm(1)), 15: cm(norm(2)), 20: cm(norm(3)), 25: cm(norm(4)), 30: cm(norm(5)), 50: cm(norm(6))}
marker_dic = {5: 'o', 10: 'o', 15: 'o', 20: 'o', 25: 'o', 30: 'o', 50: 'o'}


# create figures
#fig1, ax1 = plt.subplots(figsize=(8 / 2.54, 5 / 2.54), dpi=300)
fig1, ax1 = plt.subplots(1, 2, figsize=(20 / 2.54, 15 / 2.54))

ax1[0].set_xlabel("Voltage ($V$)")
ax1[0].set_ylabel("Current ($A$)")
ax1[0].ticklabel_format(axis='both', style='sci', scilimits=(0, 0))
#ax1[1].set_xlabel("Device area ($m^{-2})$")
ax1[1].set_ylabel("R (k$\Omega$)")
ax1[1].ticklabel_format(axis='both', style='sci', scilimits=(0, 0))

area = np.array([])
diam = np.array([])
res = np.array([])

df = pd.DataFrame(data=None, columns=["chip", "device", "diameter", "area", "resistance"], index=None)

for x in data2load:

    for y in x[1]:

        path = rf"{main}\{x[0]}\{y}\iv"
        files = [x for x in os.listdir(path) if x.endswith(".data")]

        for z in files:

            # region ----- LOAD FILE AND EXTRACT DATA -----
            print(rf"Loading {path}\{z}... ", end="")
            path = rf"{main}\{x[0]}\{y}\iv\{z}"
            with open(path, "rb") as file:
                fet = pickle.load(file)
                print("Done")
            # endregion

            # region ----- FILTER DATA -----
            print("Filtering data... ", end="")
            if sweep_vds == 0:
                pass
            if sweep_vds == 1 and fet.data.data.shape[1] > 1:
                fet.data.data = FET.Sweep.filter_vds_fwd_sweep(fet.data)
            elif sweep_vds == 2 and fet.data.data.shape[1] > 1:
                fet.data.data = FET.Sweep.filter_vds_bkw_sweep(fet.data)
            print("Done.")  # endregion

            xdata = fet.data.data[0, :, 2]
            ydata = fet.data.data[0, :, 3]

            # fit
            fit_coef = np.polyfit(xdata, ydata, 1)
            fit_fun = np.poly1d(fit_coef)
            fit_eval = fit_fun(xdata)

            resistance = 1/fit_coef[0]

            row = {"chip": x[0], "device":y, "diameter": device_dic[y[0]], "area": np.pi*(device_dic[y[0]]/2)**2, "resistance": resistance}
            df=df.append(row, ignore_index=True)

            line_style = {'color': color_dic[device_dic[y[0]]], 'marker': 'o', 'alpha': 0.6, 'linewidth': 0, 'markeredgecolor': 'black', 'markeredgewidth': 0.1}
            ax1[0].plot(xdata, ydata, **line_style)
            ax1[0].plot(xdata, fit_eval, color='grey', linestyle='dashed')
            ax1[0].set_xlim([-0.05, 0.05])

df["resistance"] = df["resistance"] / 1e3
df.boxplot(column="resistance", ax=ax1[1])



plt.show()
