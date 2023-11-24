import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
from impedance.models.circuits import CustomCircuit
from numpy import inf, pi, mean, std

main = r"R:\Scratch\405\dabe"#r"C:"
data2load = [("au-c60-gr-resist 001", ["ei", "gi", "ii", "ki", "li", "cj"])]  # list of tuples, where the 1st element is the chip name, the 2nd is the device list
fit_range = [-inf, inf]  # define the frequency range of the fit
v_range = [[-10, 10]]  # bias voltage to plot and/or fit
compensation = False  # open-short compensation (No Load)
fit = True
model = "p(R0,C0)"
takeR0atDC = [True, 1000]  # [Bool, Hz] if takeR0atDC is True, R0 is set to the average of |Z| from 0 Hz to 'x' Hz
fitR0 = False  # True not implemented yet. Should run across different resistance values and select the best fit.
bounds = ([1e-14], [1e-13])


# region ----- Init figure -----
fig1 = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
fig2 = plt.figure(figsize=(22.5 / 2.54, 25 / 2.54))
grid1 = GridSpec(nrows=2, ncols=2)
grid2 = GridSpec(nrows=3, ncols=1)
# fig1.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0., wspace=0.)
# fig2.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0., wspace=0.)
norm_v = Normalize(vmin=np.min(v_range), vmax=np.max(v_range))
cm = get_cmap("RdYlBu_r")
ax0 = fig1.add_subplot(grid1[0, 0])
ax0.set_xlabel("Frequency (Hz)")
ax0.set_ylabel(r"|Z| ($\Omega$)")
ax1 = fig1.add_subplot(grid1[1, 0])
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel(r"$\Phi$ (°)")  # endregion
ax2 = fig1.add_subplot(grid1[0, 1])
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel(r"$(|Z|_{fit} - |Z|_{meas}) / |Z|_{meas}$")
ax3 = fig1.add_subplot(grid1[1, 1])
ax3.set_xlabel("Frequency (Hz)")
ax3.set_ylabel(r"$\Phi_{fit} - \Phi_{meas}$ (°)")
ax4 = fig2.add_subplot(grid2[0])
ax4.set_xlabel("Bias (V)")
ax4.set_ylabel(r"R ($\Omega$)")
ax5 = fig2.add_subplot(grid2[1])
ax5.set_xlabel("Bias (V)")
ax5.set_ylabel("C (F)")
ax6 = fig2.add_subplot(grid2[2])
ax6.set_xlabel("Bias (V)")
ax6.set_ylabel("Cut off (Hz)")


# region ----- Define supporting functions -----
def make_complex(r, p):
    x = r * np.cos(p * np.pi / 180)
    y = r * np.sin(p * np.pi / 180)
    return x + 1j * y
#endregion


for x in data2load:
    for y in x[1]:

        if compensation is True:
            try:
                file = [x for x in os.listdir(rf"{main}\{x[0]}\a{y[1]}\impedance analysis") if x.endswith(".bin")][0]
                print(rf"CHIP: {x[0]}, DEVICE: {y}. Loading compensation OPEN data... ", end="")
                with open(rf"{main}\{x[0]}\a{y[1]}\impedance analysis\{file}", "rb") as f:
                    data_open = pickle.load(f)
                    z_open = make_complex(data_open["data"]["impedance_modulus"], data_open["data"]["impedance_phase"])
                print("Done.")
            except FileNotFoundError:
                exit("Cannot find compensation OPEN data")
            try:
                file = [x for x in os.listdir(rf"{main}\{x[0]}\b{y[1]}\impedance analysis") if x.endswith(".bin")][0]
                print(rf"CHIP: {x[0]}, DEVICE: {y}. Loading compensation SHORT data... ", end="")
                with open(rf"{main}\{x[0]}\b{y[1]}\impedance analysis\{file}", "rb") as f:
                    data_short = pickle.load(f)
                    z_short = make_complex(data_short["data"]["impedance_modulus"], data_short["data"]["impedance_phase"])
                print("Done.")
            except FileNotFoundError:
                exit("Cannot find compensation SHORT data")

        files = [x for x in os.listdir(rf"{main}\{x[0]}\{y}\impedance analysis") if x.endswith(".bin")]
        for z in files:
            with open(rf"{main}\{x[0]}\{y}\impedance analysis\{z}", "rb") as file:
                data = pickle.load(file)
                if any([interval[0] <= data["bias"] <= interval[1] for interval in v_range]):
                    print(rf"CHIP: {x[0]}, DEVICE: {y}. Loading measurement data: {z}... ", end="")
                    z_meas = make_complex(data["data"]["impedance_modulus"], data["data"]["impedance_phase"])
                    frequency = np.array(data["data"]["frequency"])
                    print("Done.")
                else:
                    continue

            if compensation is True:
                z_comp = (z_meas - z_short) / (1 - (z_meas - z_short) * 1/z_open)

            if fit is True:
                if compensation is False:
                    print("Fitting measured data... ", end="")
                    z_meas2fit = z_meas.real[(frequency <= fit_range[1]) & (frequency >= fit_range[0])] + 1j*z_meas.imag[(frequency <= fit_range[1]) & (frequency >= fit_range[0])]
                    frequency2fit = frequency[(frequency <= fit_range[1]) & (frequency >= fit_range[0])]
                    if fitR0 is True:
                        initial_guess = [abs(z_meas)[0], 1e-15]
                        customCircuit = CustomCircuit(initial_guess=initial_guess, circuit=model)
                        z_fit = customCircuit.fit(frequency2fit, z_meas2fit, weight_by_modulus=True, bounds=([abs(z_meas)[0] * 0.1, 1e-15], [abs(z_meas)[0] * 10, 1e-11]))
                    elif fitR0 is False:
                        initial_guess = [1e-15]
                        customCircuit = CustomCircuit(initial_guess=initial_guess, circuit=model, constants={"R0": mean(abs(z_meas[frequency<=takeR0atDC[1]]))} if takeR0atDC[0] else None)
                        z_fit = customCircuit.fit(frequency2fit, z_meas2fit, weight_by_modulus=True, bounds=([1e-15], [1e-11]))
                    z_eval = customCircuit.predict(use_initial=False, frequencies=frequency2fit)

                    ax0.loglog(frequency, abs(z_meas), 'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.1, label=data["bias"])
                    ax0.loglog(frequency2fit, abs(z_eval), '--', linewidth=1, color=cm(norm_v(data["bias"])), alpha=1)
                    ax1.semilogx(frequency, np.angle(z_meas, deg=True), 'o', linewidth=0,  markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.1)
                    ax1.semilogx(frequency2fit, np.angle(z_eval, deg=True), '--', linewidth=1, color=cm(norm_v(data["bias"])), alpha=1)
                    ax2.loglog(frequency2fit, abs(abs(z_eval) / abs(z_meas2fit) - 1),'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.1)
                    ax3.semilogx(frequency2fit, np.angle(z_eval, deg=True) - np.angle(z_meas2fit, deg=True),'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.1)

                    ax4.errorbar(x=data["bias"], y=mean(abs(z_meas[frequency<=takeR0atDC[1]])), yerr=std(abs(z_meas[frequency<=takeR0atDC[1]])), marker='o', markerfacecolor=cm(norm_v(data["bias"])), markeredgecolor="black", alpha=0.5, capsize=3, color=cm(norm_v(data["bias"])))
                    ax4.set_yscale('log')
                    ax5.errorbar(x=data["bias"], y=customCircuit.parameters_[0], yerr=customCircuit.conf_[0], marker='o', markerfacecolor=cm(norm_v(data["bias"])), markeredgecolor="black", alpha=0.5, capsize=3, color=cm(norm_v(data["bias"])))
                    error = 1 / 2 / pi / abs(z_meas)[0] * (customCircuit.conf_[0] / customCircuit.parameters_[0]**2)
                    ax6.errorbar(x=data["bias"], y=1 / (2 * pi * customCircuit.parameters_[0] * abs(z_meas)[0]), yerr=error, marker='o', markerfacecolor=cm(norm_v(data["bias"])), markeredgecolor="black", alpha=0.5, capsize=3, color=cm(norm_v(data["bias"])))
                    ax6.set_yscale('log')

                if compensation is True:
                    print("Fitting compensated data... ", end="")
                    z_comp2fit = z_comp.real[(frequency <= fit_range[1]) & (frequency >= fit_range[0])] + 1j*z_comp.imag[(frequency <= fit_range[1]) & (frequency >= fit_range[0])]
                    frequency2fit = frequency[(frequency <= fit_range[1]) & (frequency >= fit_range[0])]
                    if fitR0 is True:
                        initial_guess = [abs(z_meas)[0], 1e-15]
                        customCircuit = CustomCircuit(initial_guess=initial_guess, circuit=model)
                    elif fitR0 is False:
                        initial_guess = [1e-15]
                        customCircuit = CustomCircuit(initial_guess=initial_guess, circuit=model, constants={"R0": mean(abs(z_comp[frequency<=takeR0atDC[1]]))} if takeR0atDC[0] else None)
                    z_fit = customCircuit.fit(frequency2fit, z_comp2fit, weight_by_modulus=True, bounds=([1e-15], [1e-11]))
                    z_eval = customCircuit.predict(use_initial=False, frequencies=frequency2fit)
                    ax0.loglog(frequency, abs(z_comp), 'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.1)
                    ax0.loglog(frequency2fit, abs(z_eval), '--', linewidth=1, color=cm(norm_v(data["bias"])), alpha=1)
                    ax1.semilogx(frequency, np.angle(z_meas, deg=True), 'o', linewidth=0,  markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.1)
                    ax1.semilogx(frequency2fit, np.angle(z_eval, deg=True), '--', linewidth=1, color=cm(norm_v(data["bias"])), alpha=1)
                    ax2.loglog(frequency2fit, abs(abs(z_eval) / abs(z_comp2fit) - 1),'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.1)
                    ax3.semilogx(frequency2fit, np.angle(z_eval, deg=True) - np.angle(z_comp2fit, deg=True),'o', linewidth=0, markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.1)

                    ax4.errorbar(x=data["bias"], y=mean(abs(z_comp[frequency<=takeR0atDC[1]])), yerr=std(abs(z_comp[frequency<=takeR0atDC[1]])), marker='o', markerfacecolor=cm(norm_v(data["bias"])), markeredgecolor="black", alpha=0.5, capsize=3, color=cm(norm_v(data["bias"])))
                    ax4.set_yscale('log')
                    ax5.errorbar(x=data["bias"], y=customCircuit.parameters_[0], yerr=customCircuit.conf_, marker='o', markerfacecolor=cm(norm_v(data["bias"])), markeredgecolor="black", alpha=0.5, capsize=3, color=cm(norm_v(data["bias"])))
                    ax6.semilogy(data["bias"], 1 / (2 * pi * customCircuit.parameters_[0] * abs(z_comp)[0]), 'o', linewidth=0,  markeredgecolor="black", markerfacecolor=cm(norm_v(data["bias"])), alpha=0.5)
                    ax6.set_yscale('log')

                print("Done.")
                print(z_fit)

plt.show()