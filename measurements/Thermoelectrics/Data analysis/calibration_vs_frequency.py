import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib
import numpy as np
from scipy.optimize import curve_fit
# from Thermoelectrics.Data_analysis.functions import sinfunc, cosfunc
import pickle

main = r"C:/Data"
chip = "tep_ch5_00"
device = "c3"
# arrange folder names in freqeuncy sweep as [(th1, th2, a1th1, a1th2), (th1, th2, a1th1, a1th2), ...]
sweeps = [("2022-05-12 13.15.50 - tep_ch5_00 - c3 - calibration vs frequency", "2022-05-14 00.40.08 - tep_ch5_00 - c3 - calibration vs frequency", 0.1719, 0.1748)]
          #("2021-11-24 14.42.22", "2021-11-24 09.32.50", 0.1285, 0.1287),
          #("2021-11-26 11.02.06", "2021-11-26 16.37.24", 0.1570, 0.155)]
# arrange folder names in stabilty diagrams as [(), ()]
sds = [()]
tmin, tmax = 99, 309
i_h = [1e-3, 2e-3, 3e-3]
normalize_plots = True

t_h = [293]
f_range = [1, 1e3]  # freq range (in Hz)

fit = False
r = 1e-6
dr = 1e-6
f0 = 100 * 1e-3 * 1e-3 / 2e-6

# region ----- Init figure -----
c = matplotlib.cm.get_cmap("RdYlBu_r")
norm = matplotlib.colors.Normalize(vmin=0, vmax=3e-3)
fig = plt.figure(figsize=(24 / 2.54, 15 / 2.54))
fig.subplots_adjust(top=0.95, bottom=0.11, left=0.1, right=1.0, hspace=0.25, wspace=1.0)
grid = matplotlib.gridspec.GridSpec(nrows=2, ncols=10)
# ------------------------------------
ax1 = fig.add_subplot(grid[0, 0:3])
ax1.set_xlabel("f (Hz)")
ax1.set_ylabel("$\Delta T_{x}$ (°C)" if normalize_plots is False else "$\Delta T_{x}/\Delta T_{x,max}$")
ax12 = ax1.twinx()
ax12.set_ylabel(r"$\alpha_x$ (V/K)" if normalize_plots is False else r"$\alpha_x/\alpha_{x,max}$")
ax13 = ax1.twinx()
ax13.set_ylabel(r"$G_x$ (S)" if normalize_plots is False else r"$G_x/G_{x,max}$")
ax13.spines["right"].set_position(("axes", 1.4))
# Having been created by twinx, par2 has its frame off, so the line of its
# detached spine is invisible.  First, activate the frame but make the patch
# and spines invisible.
#make_patch_spines_invisible(par2)
# Second, show the right spine.
#par2.spines["right"].set_visible(True)
# ------------------------------------
ax2 = fig.add_subplot(grid[1, 0:3])
ax2.set_xlabel("f (Hz)")
ax2.set_ylabel("$\Delta T_{y}$ (°C)" if normalize_plots is False else "$\Delta T_{y}/\Delta T_{y,max}$")
ax22 = ax2.twinx()
ax22.set_ylabel(r"$\alpha_y$ (V/K)" if normalize_plots is False else r"$\alpha_y/\alpha_{y,max}$")
ax23 = ax2.twinx()
ax23.set_ylabel(r"$G_y$ (S)" if normalize_plots is False else r"$G_y/G_{y,max}$")
ax23.spines["right"].set_position(("axes", 1.4))
# ------------------------------------
ax3 = fig.add_subplot(grid[0, 5:8])
ax3.set_xlabel("f (Hz)")
ax3.set_ylabel("$|\Delta T|$ (°C)" if normalize_plots is False else "$|\Delta T|/|\Delta T_{max}|$")
ax32 = ax3.twinx()
ax32.set_ylabel(r"$|\alpha|$ (V/K)" if normalize_plots is False else r"$|\alpha|/|\alpha_{max}|$")
ax33 = ax3.twinx()
ax33.set_ylabel(r"$|G|$ (S)" if normalize_plots is False else r"$|G|/|G_{max}|$")
ax33.spines["right"].set_position(("axes", 1.4))
# ------------------------------------
ax4 = fig.add_subplot(grid[1, 5:8])
ax4.set_xlabel("f (Hz)")
ax4.set_ylabel(r"arg($\Delta T$)")
ax42 = ax4.twinx()
ax42.set_ylabel(r"arg($\alpha)$")
ax43 = ax4.twinx()
ax43.set_ylabel(r"arg($G$)")
ax43.spines["right"].set_position(("axes", 1.4))
# endregion

# region ----- Load files -----
for idx, experiment in enumerate(sweeps):

    path1 = rf"{main}\{chip}\{device}\calibration vs frequency\{experiment[0]}.data"
    path2 = rf"{main}\{chip}\{device}\calibration vs frequency\{experiment[1]}.data"

    print(f"Loading experiment {path1}... ", end="")
    with open(path1, "rb") as f:
        data1 = pickle.load(f)
    if data1.data.t[0]["dr"]["h1"] is not None:
        data1 = data1.data.t[0]["dr"]["h1"]
    elif data1.data.t[0]["dr"]["h2"] is not None:
        data1 = data1.data.t[0]["dr"]["h2"]
    print("Done.")

    print(f"Loading experiment {path2}... ", end="")
    with open(path2, "rb") as f:
        data2 = pickle.load(f)
    if data2.data.t[0]["dr"]["h1"] is not None:
        data2 = data2.data.t[0]["dr"]["h1"]
    elif data2.data.t[0]["dr"]["h2"] is not None:
        data2 = data2.data.t[0]["dr"]["h2"]
    print("Done.")  # endregion

    if len(data2) != len(data1) or len(data1[0]) != len(data2[0]):
        exit("Files length mismatch.")

    for idx1 in range(len(data1)):
        f = np.zeros(len(data1[0]))
        x1 = np.zeros(len(data1[0]))
        y1 = np.zeros(len(data1[0]))
        x2 = np.zeros(len(data1[0]))
        y2 = np.zeros(len(data1[0]))
        if data1[idx1][0]["i_h"] in i_h or i_h == []:
            for idx2 in range(len(data1[0])):
                i = data1[idx1][idx2]["i_h"]
                f[idx2] = data1[idx1][idx2]["f"]
                x1[idx2] = data1[idx1][idx2]["drt1"].x_avg / experiment[2]
                y1[idx2] = data1[idx1][idx2]["drt1"].y_avg / experiment[2]
                x2[idx2] = data2[idx1][idx2]["drt2"].x_avg / experiment[3]
                y2[idx2] = data2[idx1][idx2]["drt2"].y_avg / experiment[3]
            x1 = x1[(f >= f_range[0]) & (f <= f_range[1])]
            y1 = y1[(f >= f_range[0]) & (f <= f_range[1])]
            x2 = x2[(f >= f_range[0]) & (f <= f_range[1])]
            y2 = y2[(f >= f_range[0]) & (f <= f_range[1])]
            f = f[(f >= f_range[0]) & (f <= f_range[1])]
            dtx = x1 - x2
            dty = (y1 - y2)

            ax1.semilogx(f, dtx if normalize_plots is False else dtx / max(dtx), label="amplitude", linewidth=0, marker="o", markersize=5, color=c(norm(i)), markeredgecolor="black", alpha=0.5)
            ax2.semilogx(f, dty if normalize_plots is False else dty / max(dty), label="amplitude", linewidth=0, marker="D", markersize=5, color=c(norm(i)), markeredgecolor="black", alpha=0.5)
            ax3.semilogx(f, np.sqrt(dtx**2 + dty**2) if normalize_plots is False else np.sqrt(dtx**2 + dty**2) / max(np.sqrt(dtx**2 + dty**2)), label="amplitude", linewidth=0, marker="o", markersize=5, color=c(norm(i)), markeredgecolor="black", alpha=0.5)
            ax4.semilogx(f, np.rad2deg(np.arctan(dty/dtx)), label="amplitude", linewidth=0, marker="D", markersize=5, color=c(norm(i)), markeredgecolor="black", alpha=0.5)

    if fit is True:
        ''' Fitting '''
        # kn(n, x) is the modified Bessel function (of x) of the second kind of order n
        # to fit complex data one must create ff and yy, i.e. concatenated arrays of real and imaginary values
        # p0 is the initial guess
        # The model function, f(x, …) must take the independent variable as the first argument
        # and the parameters to fit as separate remaining arguments.
        popt, pcov = curve_fit(sinfunc, f, x) # x and y are my data points
        ax3.semilogx(f, sinfunc(f, popt[0], popt[1], popt[2], popt[3], popt[4]), label="x")
        # ax3.semilogx(f, sinfunc(f, 8.3e-7, f0, 5, r, dr), label="x")
        # ax3.semilogx(f, cosfunc(f, 8.3e-7, f0, 5, r, dr), label="y")
        # w = 2 * np.pi * f
        # q = np.sqrt(1j * 2 * w / K)
        # T = 2 * f0 / (4 * np.pi * k) * np.imag(K0(q * r)) * np.sin(2 * w * t)
        # T = - 2 * f0 / (4 * np.pi * k) * np.real(K0(q * r)) * np.cos(2 * w * t)

        # f0 is the time-independent-component energy dissipated per unit length and time
        # f0 = R0 * I0 ** 2
        # dTx = f0 / (4 * np.pi * k) * np.imag(K0(q * r))
        # dTy = - f0 / (4 * np.pi * k) * np.real(K0(q * r))



plt.show()


