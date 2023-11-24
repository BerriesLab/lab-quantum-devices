import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
from impedance.models.circuits import CustomCircuit
from numpy import inf, pi, mean, std
import pandas as pd

main = r"T:"
data2load = [("qd_gr_00", ["ad", "bf", "cd", "ce", "cg",
                           "df", "dg", "dh",
                           "fd", "ff", "fg", "gc", "gi",
                           "hd", "hf", "hi", "if", "ii", "je", "jg", "jh",
                           "le",
                           "me",
                           "od"])]

data2load = [("qd_gr_00", ["bf"])]

def takeR0atDC(z, n):
    return mean(abs(z)[0: n])

fit_range = [-inf, inf]  # define the frequency range of the fit
v_range = [[-0.5, 0.5]]  # bias voltage to plot and/or fit
compensation = True # open-short compensation (No Load)
fit = True  # if fit is False takes R0 at DC by averaging from min(f) to 100 Hz
model = "p(R0,C0)-R1"
fitR0 = True
initial_guess = [None, 1e-12]
bounds = ([10e3, 1e-15], [10e7, 1e-11])
Rs = np.logspace(4, 5, 100)

device_dic = {'a': 5, 'b': 5, 'c': 5, 'd': 10, 'e': 10, 'f': 15, 'g': 15, 'h': 20, 'i': 20, 'j': 20, 'k': 25, 'l': 25,
              'm': 30, 'n': 30, 'o': 50, 'p': 50, 'q': 50}

# to ise only open/short from 1st row of group
firstRow = True
file2search = {"a": "a",
               "b": "a",
               "c": "a",
               "d": "d",
               "e": "d",
               "f": "f",
               "g": "f",
               "h": "h",
               "i": "h",
               "j": "h",
               "k": "k",
               "l": "k",
               "m": "m",
               "n": "m",
               "o": "o",
               "p": "o",
               "q": "o"}


# region ----- Init figure -----
fig1 = plt.figure(figsize=(16 / 2.54, 22.5 / 2.54))  # Z vs frequency
# fig2 = plt.figure(figsize=(35 / 2.54, 22.5 / 2.54))  # Z vs frequency error
fig2 = plt.figure(figsize=(15 / 2.54, 25 / 2.54))
fig3 = plt.figure(figsize=(12 / 2.54, 10 / 2.54))
grid1 = GridSpec(nrows=2, ncols=1)
grid2 = GridSpec(nrows=3, ncols=1)
grid3 = GridSpec(nrows=1, ncols=1)
grid1.update(top=0.97, bottom=0.11, left=0.125, right=0.925, hspace=0.25, wspace=0.2)
grid2.update(top=0.97, bottom=0.11, left=0.125, right=0.925, hspace=0.25, wspace=0.2)
grid3.update(top=0.92, bottom=0.135, left=0.12, right=0.925, hspace=0.2, wspace=0.2)
normstat = Normalize(vmin=0, vmax=int(sum([len(x[1]) for x in data2load])))
normdiam = Normalize(vmin=5, vmax=50)
normbias = Normalize(vmin=np.min(v_range), vmax=np.max(v_range))
cm = get_cmap("RdYlBu_r")
ax0 = fig1.add_subplot(grid1[0])
ax0.set_xlabel("Frequency (Hz)")
ax0.set_ylabel(r"|Z| ($\Omega$)")
ax1 = fig1.add_subplot(grid1[1])
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel(r"$\Phi$ (°)")
ax1.set_ylim([-100, 10])
# ax2 = fig1.add_subplot(grid1[0, 1])
# ax2.set_xlabel("Frequency (Hz)")
# ax2.set_ylabel(r"$(|Z|_{fit} - |Z|_{meas}) / |Z|_{meas}$")
# ax3 = fig1.add_subplot(grid1[1, 1])
# ax3.set_xlabel("Frequency (Hz)")
# ax3.set_ylabel(r"$\Phi_{fit} - \Phi_{meas}$ (°)")
ax4 = fig2.add_subplot(grid2[0])
ax4.set_xlabel("Bias (V)")
ax4.set_ylabel("R ($\Omega m^2$)")
ax4.set_yscale('log')
ax5 = fig2.add_subplot(grid2[1])
ax5.set_xlabel("Bias (V)")
ax5.set_ylabel("C (F/$m^2$)")
ax5.set_yscale('log')
ax6 = fig2.add_subplot(grid2[2])
ax6.set_xlabel("Bias (V)")
ax6.set_ylabel("Cut off (Hz)")
ax6.set_yscale('log')
ax7 = fig3.add_subplot(grid3[0, 0])
ax7.set_xlabel("Re{Z}")
ax7.set_ylabel("Im{Z}")
plt.show(block=False)
plt.pause(0.25)
# endregion

# region ----- Define supporting functions -----
def make_complex(r, p):
    x = r * np.cos(p * np.pi / 180)
    y = r * np.sin(p * np.pi / 180)
    return x + 1j * y
#endregion

df = pd.DataFrame(columns=["chip", "device", "v", "r", "r_err", "c", "c_err", "f", "f_err"], index=None)
m = 0
for x in data2load:
    for y in x[1]:
        if compensation is True:

            file = [x for x in os.listdir(rf"{main}\{x[0]}\{file2search[y[0]]}a\impedance analysis") if x.endswith(".bin")][0]
            print(rf"CHIP: {x[0]}, DEVICE: {y}. Loading compensation OPEN data... ", end="")
            with open(rf"{main}\{x[0]}\{file2search[y[0]]}a\impedance analysis\{file}", "rb") as f:
                data_open = pickle.load(f)
                z_open = make_complex(data_open["data"]["impedance_modulus"], data_open["data"]["impedance_phase"])
            print("Done.")

            file = [x for x in os.listdir(rf"{main}\{x[0]}\{file2search[y[0]]}b\impedance analysis") if x.endswith(".bin")][0]
            print(rf"CHIP: {x[0]}, DEVICE: {y}. Loading compensation SHORT data... ", end="")
            with open(rf"{main}\{x[0]}\{file2search[y[0]]}b\impedance analysis\{file}", "rb") as f:
                data_short = pickle.load(f)
                z_short = make_complex(data_short["data"]["impedance_modulus"], data_short["data"]["impedance_phase"])
            print("Done.")

        files = [x for x in os.listdir(rf"{main}\{x[0]}\{y}\impedance analysis") if x.endswith(".bin")]

        for idx, z in enumerate(files):
            with open(rf"{main}\{x[0]}\{y}\impedance analysis\{z}", "rb") as file:
                data = pickle.load(file)
                if any([interval[0] <= data["bias"] <= interval[1] for interval in v_range]):
                    print(rf"CHIP: {x[0]}, DEVICE: {y}. Loading measurement data: {z}... ", end="")
                    z_meas = make_complex(data["data"]["impedance_modulus"], data["data"]["impedance_phase"])
                    frequency = np.array(data["data"]["frequency"])
                    print("Done.")
                else:
                    continue

            # Assign z_measured or z_compensated to z. From now on only z is used
            if compensation is True:
                z = (z_meas - z_short) / (1 - (z_meas - z_short)/z_open)
            if compensation is False:
                z = z_meas

            # Plot experimental data
            # ax0.loglog(frequency, abs(z), 'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_s(data["bias"])), alpha=0.5, label=f"{data['bias']:.2f} V")
            # ax1.semilogx(frequency, np.angle(z, deg=True), 'o', linewidth=0,  markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.5, label=f"{data['bias']:.2f} V")
            ax0.loglog(frequency, abs(z), 'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(normdiam(device_dic[y[0]])), alpha=0.5, label=f"{device_dic[y[0]]} $\mu m$")
            ax1.semilogx(frequency, np.angle(z, deg=True), 'o', linewidth=0,  markeredgecolor="black", markerfacecolor=cm(normdiam(device_dic[y[0]])), alpha=0.5, label=f"{device_dic[y[0]]} $\mu m$")

            if fit is True:
                print("Fitting measured data... ", end="")
                z2fit = z.real[(frequency <= fit_range[1]) & (frequency >= fit_range[0])] + 1j*z.imag[(frequency <= fit_range[1]) & (frequency >= fit_range[0])]
                frequency2fit = frequency[(frequency <= fit_range[1]) & (frequency >= fit_range[0])]
                temp = []
                for idx_r1, val_r1 in enumerate(Rs if device_dic[y[0]]>5 else [0]):
                    initial_guess[0] = abs(z)[0]
                    customCircuit = CustomCircuit(initial_guess=initial_guess, circuit=model, constants={"R1": val_r1})
                    z_fit = customCircuit.fit(frequency2fit, z2fit, weight_by_modulus=True, bounds=bounds)
                    z_eval = customCircuit.predict(use_initial=False, frequencies=frequency2fit)
                    err = frequency2fit*(np.angle(z_eval) - np.angle(z2fit))**2
                    temp.append((val_r1, sum(err)))
                min_err = min([x[1] for x in temp])
                for val in temp:
                    if val[1] == min_err:
                        val_r1 = val[0]
                initial_guess[0] = abs(z)[0]
                customCircuit = CustomCircuit(initial_guess=initial_guess, circuit=model, constants={"R1": val_r1})
                z_fit = customCircuit.fit(frequency2fit, z2fit, weight_by_modulus=True, bounds=bounds)
                z_eval = customCircuit.predict(use_initial=False, frequencies=frequency2fit)

                # ax0.loglog(frequency2fit, abs(z_eval), '--', linewidth=1.2, color=cm(norm_v(data["bias"])), alpha=1)
                # ax1.semilogx(frequency2fit, np.angle(z_eval, deg=True), '--', linewidth=1.2, color=cm(norm_v(data["bias"])), alpha=1)
                ax0.loglog(frequency2fit, abs(z_eval), '--', linewidth=1.2, color=cm(normdiam(device_dic[y[0]])), alpha=1)
                ax1.semilogx(frequency2fit, np.angle(z_eval, deg=True), '--', linewidth=1.2, color=cm(normdiam(device_dic[y[0]])), alpha=1)
                # ax2.loglog(frequency2fit, abs(abs(z_eval) / abs(z2fit) - 1),'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.5)
                # ax3.semilogx(frequency2fit, np.angle(z_eval, deg=True) - np.angle(z2fit, deg=True),'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.5)

                print("Done.")
                plt.pause(0.1)

                r_err = std(abs(z[frequency<=100]))
                c_err = customCircuit.conf_[0]
                df=df.append({"chip": x[0],
                              "device": y,
                              "diameter": device_dic[y[0]],
                              "area": pi*((device_dic[y[0]]*1e-6)/2)**2,
                              "v": data["bias"],
                              "r": customCircuit.parameters_[0],
                              "r_err": customCircuit.conf_[0],
                              "c":customCircuit.parameters_[1],
                              "c_err": customCircuit.conf_[1],
                              "rs": val_r1,
                              "rs_err": None,
                              "f": 1 / (2 * pi * customCircuit.parameters_[1] * abs(z)[0]),
                              "f_err": 1 / (2 * pi) * np.sqrt((r_err/customCircuit.parameters_[1]/customCircuit.parameters_[0]**2)**2 +
                                                              (c_err/customCircuit.parameters_[1]**2/customCircuit.parameters_[0])**2)}, ignore_index=True)

                # ax7.plot(z.real[frequency > 1000], -z.imag[frequency > 1000], 'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.4, label=f"{data['bias']:.2f} V")
                # ax7.plot(np.real(z_eval), -np.imag(z_eval), '--', linewidth=2, color=cm(norm_v(data["bias"])))



if fit is True:
    df.to_csv(rf"{main}\impedance_data_summary.csv", index=False)
    grouped = df.sort_values(["v"]).groupby(["chip", "device", "area"])
    m = 0
    for name, group in grouped:
        ax4.errorbar(x=group.v.values, y=group.r.values*group.area.values, yerr=group.r_err.values, linewidth=1, marker='o', markerfacecolor=cm(normstat(m)), markeredgecolor="black", alpha=0.5, capsize=3, color=cm(normstat(m)))
        ax5.errorbar(x=group.v.values, y=group.c.values/group.area.values, yerr=group.c_err.values, linewidth=1, marker='o', markerfacecolor=cm(normstat(m)), markeredgecolor="black", alpha=0.5, capsize=3, color=cm(normstat(m)))
        ax6.errorbar(x=group.v.values, y=group.f.values, yerr=group.f_err.values, linewidth=1, marker='o', markerfacecolor=cm(normstat(m)), markeredgecolor="black", alpha=0.5, capsize=3, color=cm(normstat(m)))
        m = m + 1
    ax6.axhline(y=1e6, xmin=0, xmax=1, linestyle="-.")
    ax7.legend(frameon=True, framealpha=1)
ax0.legend(frameon=True, framealpha=1, loc="lower left")
ax1.legend(frameon=True, framealpha=1, loc="lower left")
plt.show()