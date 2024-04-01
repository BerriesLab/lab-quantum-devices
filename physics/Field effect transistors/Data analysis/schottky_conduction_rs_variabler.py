import pickle
import os
from Objects.measurement import FET
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
import matplotlib.cm
from scipy import constants

# style
VERY_SMALL_SIZE = 4
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

matplotlib.rc('font', size=SMALL_SIZE)  # controls default text sizes
matplotlib.rc('axes', titlesize=SMALL_SIZE)  # fontsize of the axes title
matplotlib.rc('axes', labelsize=SMALL_SIZE)  # fontsize of the x and y labels
matplotlib.rc('xtick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
matplotlib.rc('ytick', labelsize=SMALL_SIZE)  # fontsize of the tick labels
matplotlib.rc('legend', fontsize=SMALL_SIZE)  # legend fontsize
matplotlib.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

main = r"T:\Data\Processed data"

devices2load = ["cc", "ci", "bi", "ai", "bc",  # air
                # "ec", "ei", "di", "dd", "ee",
                # "gi", "gc", "fc", "fd", "ge",
                # "hi", "ii", "ie", "id", "jd",
                # "ki", "li", "le", "lf", "kf",
                # "mi", "ni", "mf", "ne", "nf",
                # "qf", "pe", "od", "pd"
                ]

devices2load = ["cf", "bf", "af", "bh", "bd",  # vacuum
                "ei", "dh", "dg", "ef", "ee",
                "gf", "gg", "gi", "fh", "fg",
                # "hg", "hh", "jh", "jf", "if",
                # "kf", "kh", "lh", "lf", "le",
                # "mf", "mh", "mi", "ni", "nf",
                # "qg", "qf", "pe", "pd", "pc"
                ]

devices2load = [#"bf", "cf", "af", "bh", "bd",
                #"dg", "dh", "ei", "ef", "ee",
                "fg", "gi", "fh", "gg", "gf",
                #"hh", "hi", "jh", "jf", "if",
                #"kf", "kh", "lh", "lf", "le",
                #"mf", "mh", "mi", "ni", "nf",
                #"pc", "pd", "pe", "qf", "qg" #"hg"
                ]  # annealed

#devices2load = ["bf", "dg", "fg", "hh", "kh", "mi", "pc"] #, "mi", "pc"]
devices2load = ["hh", "kh"]
##devices2load = ["bf", "dg", "fg", "hh", "kf", "mi", "qg"] #, "mi", "pc"]


data2load = [("p3ht_gr_00_annealed",
              devices2load)]  # list of tuples, where the 1st element is the chip name, the 2nd is the device list
confidence_band = False
temperature = False
cycle_vds = 0  # [int] i-th Vds cycle where to calculate mobility
sweep_vds = 2  # [int] direction of the Vds sweep where to extract the mobility: {0: all, 1: fwd, 2: bkw}

cm = matplotlib.cm.get_cmap("summer")
norm = Normalize(vmin=0, vmax=6)

device_dic = {'a': 5, 'b': 5, 'c': 5, 'd': 10, 'e': 10, 'f': 15, 'g': 15, 'h': 20, 'i': 20, 'j': 20, 'k': 25, 'l': 25,
              'm': 30, 'n': 30, 'o': 50, 'p': 50, 'q': 50}
color_dic = {5: cm(norm(0)), 10: cm(norm(1)), 15: cm(norm(2)), 20: cm(norm(3)), 25: cm(norm(4)), 30: cm(norm(5)),
             50: cm(norm(6))}
marker_dic = {5: 'o', 10: 'o', 15: 'o', 20: 'o', 25: 'o', 30: 'o', 50: 'o'}

# create figures
fig1, ax1 = plt.subplots(1, 2, figsize=(16 / 2.54, 8 / 2.54), dpi=300)

ax1[0].set_xlabel("Voltage square root $(V - JAR_{s})^{1/2}$")
ax1[0].set_ylabel("$ln(J)$ ($Am^{-2}$)")
ax1[0].ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

ax1[1].set_xlabel("Voltage ($V$)")
ax1[1].set_ylabel("Current density ($Am^{-2}$)")
ax1[1].ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

Rss = np.arange(10, 10.001e4, 10)

for x in data2load:

    for j, y in enumerate(x[1]):

        path = rf"{main}\{x[0]}\{y}\iv"
        files = [x for x in os.listdir(path) if x.endswith(".data")]

        fit_results = np.zeros(shape=(len(Rss), 7))
        results = np.zeros(shape=(len(x[1]), 8))

        for idxf, z in enumerate(files):

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

            # data
            xdata = fet.data.data[0, :, 2]  # voltage
            ydata = fet.data.data[0, :, 3]  # current

            # fixed paramters
            #Rs = 2e4
            device_area = np.pi * ((device_dic[y[0]]) * 1e-6 / 2) ** 2
            e = constants.elementary_charge
            vac_perm = constants.epsilon_0
            k = constants.k
            #richardson = 1.2e6
            pos_richardson = 4.302
            neg_richardson = 20.492
            T = 293
            thickness = 100e-9

            # Current density
            voltage = xdata
            current_density = ydata / device_area

            # find Rs that gets consistent permittivity for positive and negative polarities
            def linear_fit(fit_roi):
                fit_coef = np.polyfit(rs_voltage[fit_roi], ln_current_density[fit_roi], 1)
                fit_model = np.poly1d(fit_coef)
                return fit_coef, fit_model

            for idx, val in enumerate(Rss):
                rs_voltage = np.sqrt(np.abs(voltage - val * current_density * device_area)) * np.sign(
                    voltage - val * current_density * device_area)
                # rs_voltage = voltage
                ln_current_density = np.log(np.abs(current_density))

                pos_fit_coef, pos_fit_model = linear_fit(voltage >= 2.5)  # linear fit of the positive region
                neg_fit_coef, neg_fit_model = linear_fit(voltage <= -2.5)  # linear fit of the negative region

                pos_intercept, pos_slope = pos_fit_coef[1], pos_fit_coef[0]
                neg_intercept, neg_slope = neg_fit_coef[1], neg_fit_coef[0]

                pos_rel_permittivity = e / (4 * np.pi * vac_perm * thickness) * ((e / (pos_slope * k * T)) ** 2)
                neg_rel_permittivity = e / (4 * np.pi * vac_perm * thickness) * ((e / (neg_slope * k * T)) ** 2)

                pos_potential_barrier = k * T / e * (np.log(pos_richardson * T ** 2) - pos_intercept)
                neg_potential_barrier = k * T / e * (np.log(neg_richardson * T ** 2) - neg_intercept)

                fit_results[idx,:] = [device_dic[y[0]], device_area, val, neg_rel_permittivity, pos_rel_permittivity, neg_potential_barrier, pos_potential_barrier]

            # find permittivity
            expected_perm = 3.5
            tol = 0.5 # %
            #print(len(fit_results))
            # keep values in expected permittivity range
            fit_results = fit_results[(np.abs(fit_results[:,3] - expected_perm) < expected_perm*tol) & (np.abs(fit_results[:,4] - expected_perm) < expected_perm*tol)]
            #print(len(fit_results))
            # find poisitive and negative polarity consistent permitivity
            min_idx = np.argmin(np.abs(fit_results[:,3]-fit_results[:,4]))
            fit_results = fit_results[min_idx]
            #print(len(fit_results))
            #print(fit_results)

            print("-----------")
            print("Device: " + str(y))
            print("Device diameter: " + str(fit_results[0]))
            print("Device area: " + str(fit_results[1]))
            print("Series resistance: " + str(fit_results[2]))
            print("Positive permittivity: " + str(fit_results[4]))
            print("Negatative permittivity: " + str(fit_results[3]))
            print("Average permittivity: " + str((fit_results[3] + fit_results[4])/2))
            print("Positive barrier potential: " + str(fit_results[6]))
            print("Negatative barrier potential: " + str(fit_results[5]))
            print("-----------")
            # Rs = Rss[min_idx]

            # save results
            results[j] = [fit_results[0], fit_results[1], fit_results[2], fit_results[4], fit_results[3], (fit_results[3] + fit_results[4])/2, fit_results[6], fit_results[5]]

            # Plot Schottky
            Rs = fit_results[2]
            rs_voltage = np.sqrt(np.abs(voltage - Rs * current_density * device_area)) * np.sign(voltage - Rs * current_density * device_area)
            ln_current_density = np.log(np.abs(current_density))
            line_style = {'color': color_dic[device_dic[y[0]]], 'marker': marker_dic[device_dic[y[0]]], 'alpha': 0.8,
                          'linewidth': 0,'markeredgecolor': 'black', 'markeredgewidth': 0.1}
            ax1[0].plot(rs_voltage, ln_current_density, **line_style, label='Data')
            ax1[1].plot(voltage, current_density, **line_style)

            # Thermionic with parameters
            pos_potential_barrier = fit_results[6]
            neg_potential_barrier = fit_results[5]
            perm_r = (fit_results[3] + fit_results[4])/2
            pos_theor_current_density = pos_richardson * T ** 2 * np.exp(-e * (pos_potential_barrier - np.sqrt(e * np.abs(voltage[voltage >= 0] - Rs * current_density[voltage >= 0] * device_area) / (thickness * 4 * np.pi * vac_perm * perm_r))) / (k * T))
            neg_theor_current_density = -neg_richardson * T ** 2 * np.exp(-e * (neg_potential_barrier - np.sqrt(e * np.abs(voltage[voltage <= 0] - Rs * current_density[voltage <= 0] * device_area) / (thickness * 4 * np.pi * vac_perm * perm_r))) / (k * T))

            # # Plot log
            ax1[0].plot(rs_voltage[voltage >= 0], np.log(np.abs(pos_theor_current_density)), color='green', linestyle='--', label='Linear fit')
            ax1[0].plot(rs_voltage[voltage <= 0], np.log(np.abs(neg_theor_current_density)), color='grey', linestyle='--')

            # Plot linear
            ax1[1].plot(voltage[voltage >= 0], pos_theor_current_density, color='green', linestyle='--')
            ax1[1].plot(voltage[voltage <= 0], neg_theor_current_density, color='grey', linestyle='--')


#ax1[0, 0].legend(frameon=False, framealpha=1)

print(results)

fig1.tight_layout()  # adjust only when called, just before saving
fig_settings = {'dpi': 300, 'transparent': False, 'bbox_inches': 'tight', 'pad_inches': 0.1}
fig_path = 'T:\Data\Figures\p3ht_gr_00'
fig1.savefig(fname=fig_path + r'\thermionic.png', **fig_settings)

plt.show()
