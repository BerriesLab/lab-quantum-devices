from functions_import_mat_file import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import cm
import matplotlib, os
import scipy.stats as stats


# USER SECTION - Select measurement conditions ---------------------------------------------------------------------------------------------
temperature = 300       # select calibration bath temperature
heater = 1              # select either heater 1 or 2
zero = False            # choose either to include (True) or exclude (False) the heater current = 0 mA in the analysis
vgs = [-8, 0, 50]   # chose gate voltage values where to plot thermovoltage vs temperature difference


# Load files -------------------------------------------------------------------------------------------------------------------------------
filename = "calibration - th1 - th2 - h" + str(heater) + " - " + str(temperature) + " K.txt"
cal = np.loadtxt(fname=filename, delimiter=",", skiprows=1)     # load txt file into 2d array
file_list, iH = [], []
for file in os.listdir(os.getcwd()):
    if ("stability - h" + str(heater) + " - " + str(temperature) + " K" in file) and (file.endswith(".mat")):
        file_list.append(file)                                  # get file list
        iH.append(float(file[-10:-7]))                          # get corresponding list of heater current values


# Initialize figure ------------------------------------------------------------------------------------------------------------------------
fig1 = plt.figure(constrained_layout=False, figsize=(15/2.54, 15/2.54))  # create figure
gs1 = gridspec.GridSpec(ncols=2, nrows=len(file_list), figure=fig1)     # define grid spacing object
gs1.update(wspace=0.6, hspace=0.6)                                      # set spacing between axes.

fig2 = plt.figure(constrained_layout=False, figsize=(20/2.54, 15/2.54))  # create figure
gs2 = gridspec.GridSpec(ncols=2, nrows=2, figure=fig1)                  # define grid spacing object
gs2.update(wspace=0.4, hspace=0.3)

axGg = fig2.add_subplot(gs2[0, 0])
axGg.set_ylabel("G (S)")
axGg.set_xlabel("Gate (V)")
axGg.set_ylim([0.00005, 0.00025])
axag = fig2.add_subplot(gs2[1, 0])
axag.set_ylabel(r"$\alpha$ ($\mu$V/K)")
axag.set_xlabel("Gate (V)")
axag.set_ylim([-75, 75])
axVT = fig2.add_subplot(gs2[0, 1])
axVT.set_ylabel(r"Thermovoltage ($\mu$V)")
axVT.set_xlabel(r"$\Delta\Theta_{2\omega,\pi/2}$ (K)")
axPF = fig2.add_subplot(gs2[1, 1])
axPF.set_ylabel(r"PF (pW/m$K^2$)")
axPF.set_xlabel("Gate (V)")
axPF.set_ylim([-0.05, 0.6])


# find zmin and zmax and select
for idx, file in enumerate(file_list):  # process files in data_list iteratively
    data = loadmat(file)  # load matlab file
    i_th1 = data["IV"]["data2"][1]  # get thermocurrent matrix (quadrature component) (single sweep on the bias)
    i_G1 = data["IV"]["data2"][2]  # get amplitude matrix of externally driven current (single sweep on the bias)
    cntrGmin = np.min(i_G1) if (idx == 0) or (np.min(i_G1) < cntrGmin) else cntrGmin  # update vmin if necessary
    cntrGmax = np.max(i_G1) if (idx == 0) or (np.max(i_G1) > cntrGmax) else cntrGmax  # update vmax if necessary
    cntrTEmin = np.min(i_th1) if (idx == 0) or (np.min(i_th1) < cntrTEmin) else cntrTEmin  # update vmin if necessary
    cntrTEmax = np.max(i_th1) if (idx == 0) or (np.max(i_th1) > cntrTEmax) else cntrTEmax  # update vmax if necessary


# Initialize arrays ------------------------------------------------------------------------------------------------------------------------
x = np.zeros((len(file_list), data["IV"]["Bias2"].shape[0], len(vgs)))    # x-data for thermovoltage vs derivative plot
y = np.zeros((len(file_list), data["IV"]["Bias2"].shape[0], len(vgs)))    # y-data for thermovoltage vs dT plot [n. of slopes, bias, dT]


# Read and plot data -----------------------------------------------------------------------------------------------------------------------
for idx, file in enumerate(file_list):  # process files in data_list iteratively

    print("processing file: " + file + " ...")

    data = loadmat(file)                # load matlab file

    v_gate = data["Gate"]["voltage"]             # get gate voltage (single sweep)
    v_bias2 = data["IV"]["bias"]                 # get bias voltage values array (double sweep) in V
    v_bias1 = data["IV"]["Bias2"]*1000         # get bias voltage values array (single sweep) in V

    v_gate_0_idx = np.abs(v_gate - 0).argmin()   # get index of gate voltage = 0
    v_bias_0_idx = np.abs(v_bias1 - 0).argmin()  # get index of DC bias voltage = 0

    # i_G2 = data["IV"]["current"][2]     # get amplitude of externally driven current(double sweep on the bias), matrix [bias, gate]
    # i_G1 = data["IV"]["data2"][2]       # get amplitude of externally driven current(single sweep on the bias), matrix [bias, gate]
    # i_th2 = data["IV"]["current"][1]    # get thermocurrent matrix (quadrature component) (double sweep on the bias), matrix [bias, gate]
    G1 = data["IV"]["data2"][2]         # get conductance (single sweep on the bias), matrix [bias, gate]
    i_th1 = data["IV"]["data2"][1]      # get thermocurrent matrix (quadrature component) (single sweep on the bias), matrix [bias, gate]

    xv, yv = np.meshgrid(v_gate, v_bias1, copy=True, sparse=False, indexing='xy')           # define a mesh grid

    axG = fig1.add_subplot(gs1[idx, 0])                                                     # create axis for G stability diagram
    axG.set_title("Stability diagram") if idx == 0 else True                                # set title if first row
    axG.set_xlabel("Gate (V)")                                                              # set x label
    axG.set_ylabel("Bias (mV)")                                                             # set y label
    axG.set_xlim(xmin=min(v_gate), xmax=max(v_gate))                                        # set x limits
    axG.set_ylim(ymin=min(v_bias1), ymax=max(v_bias1))                                      # set y limits
    axG.contourf(xv, yv, i_G1, vmin=cntrGmin, vmax=cntrGmax, levels=100)                    # plot contour of G

    axTE = fig1.add_subplot(gs1[idx, 1])                                                    # create axis for TE stability diagram
    axTE.set_title("TE stability diagram") if idx == 0 else True                            # set title if first row
    axTE.set_xlabel("Gate (V)")                                                             # set x label
    axTE.set_ylabel("Bias (mV)")                                                            # set y label
    axTE.set_xlim(xmin=min(v_gate), xmax=max(v_gate))                                       # set x limits
    axTE.set_ylim(ymin=min(v_bias1), ymax=max(v_bias1))                                     # set y limits
    axTE.contourf(xv, yv, i_th1, vmin=cntrTEmin, vmax=cntrTEmax, levels=100)        # plot contour of thermovoltage

    # v_G = data["Lockin2"]["amplitude_Vbias"]          # get amplitude of externally applied AC voltage to measure G

    T1 = cal[cal[:, 0] == iH[idx]][0, 1]                # get th1 temperature drift
    T2 = cal[cal[:, 0] == iH[idx]][0, 7]                # get th2 temperature drift
    T_avg = (T1 + T2) / 2                               # calculate device average temperature
    T1_2w_pi2 = cal[cal[:, 0] == iH[idx]][0, 5]         # get th1 AC temperature amplitude (in quadrature)
    T2_2w_pi2 = cal[cal[:, 0] == iH[idx]][0, 11]        # get th2 AC temperature amplitude (in quadrature)
    dT_2w_pi2 = T1_2w_pi2 - T2_2w_pi2                   # calculate AC temperature difference amplitude
    # G = i_G1 / v_G                                    # calculate conductance matrix [bias, gate]
    # v_th = np.divide(i_th1, G) / 1E-6                 # calculate thermovoltage (quadrature component), matrix [bias, gate]
    v_th = np.divide(i_th1, G1) / 1E-6                  # calculate thermovoltage (quadrature component), matrix [bias, gate]
    alpha_pt = -8.2302 - 0.011056 * T_avg + 2212 * T_avg ** (-1) - 84652 * T_avg ** (-2)    # Seebeck of platinum in uV/K
    alpha = - v_th / (T1_2w_pi2 - T2_2w_pi2) + alpha_pt   # calculate Seebeck, matrix [bias, gate]

    pf = np.multiply(np.power(alpha * 1E-6, 2), G1)

    c = cm.RdYlBu_r  # choose color map
    norm = matplotlib.colors.Normalize(vmin=np.min(iH), vmax=np.max(iH))  # normalize color map with respect to heater current

    for index in range(0, G1.shape[0]):  # plot G vs gate traces grouped by heater current
        axGg.plot(v_gate, G1[index, :], linewidth=4, alpha=0.2,  c=c(norm(iH[idx])))

    for index in range(0, alpha.shape[0]):  # plot i_th vs gate traces grouped by heater current
        axag.plot(v_gate, alpha[index, :], linewidth=4, alpha=0.2, c=c(norm(iH[idx])))
        for vg in vgs:
            axag.axvline(x=vg, linestyle="--", color="grey")

    for index in range(0, pf.shape[0]):        # plot i_th vs gate traces grouped by heater current
        axPF.plot(v_gate, pf[index, :] * 1E12, linewidth=4, alpha=0.1, c=c(norm(iH[idx])))

    for index in range(0, v_th.shape[0]):   # index run through the DC bias voltage
        for n, vg in enumerate(vgs):        # n run through the selected gate voltages
            x[idx, index, n] = dT_2w_pi2                               # get temperature difference
            y[idx, index, n] = v_th[index, np.argmin(abs(v_gate - vg))]     # get thermovoltage

# fig1.colorbar(axG.contourf(xv, yv, i_G1, vmin=cntrGmin, vmax=cntrGmax, levels=100), ax=axG)
# fig2.colorbar(axTE.contourf(xv, yv, i_th1, vmin=cntrTEmin, vmax=cntrTEmax, levels=100), ax=axTE)

axVT.scatter(x[:, :, 0].flatten(), -y[:, :, 0].flatten(), alpha=0.2, s=50, c="orange", label=str(vgs[0]) + " V")
slope, intercept, rvalue, pvalue, stderr = stats.linregress(x[:, :, 0].flatten(), -y[:, :, 0].flatten())  # linear fit
print(slope)
print(slope+alpha_pt)
xlim = np.array(axVT.get_xlim())
axVT.plot(xlim, intercept + slope * xlim, alpha=0.4, c="orange", linestyle="--")

axVT.scatter(x[:, :, 1].flatten(), -y[:, :, 1].flatten(), alpha=0.2, s=50, c="blue", label=str(vgs[1]) + " V")
slope, intercept, rvalue, pvalue, stderr = stats.linregress(x[:, :, 1].flatten(), -y[:, :, 1].flatten())  # linear fit
print(slope)
print(slope+alpha_pt)
axVT.plot(xlim, intercept + slope * xlim, alpha=0.4, c="blue", linestyle="--")

axVT.scatter(x[:, :, 2].flatten(), -y[:, :, 2].flatten(), alpha=0.2, s=50, c="red", label=str(vgs[2]) + " V")
slope, intercept, rvalue, pvalue, stderr = stats.linregress(x[:, :, 2].flatten(), -y[:, :, 2].flatten())  # linear fit
print(slope)
print(slope+alpha_pt)
axVT.plot(xlim, intercept + slope * xlim, alpha=0.4, c="red", linestyle="--")

axVT.legend()

plt.show()


# Save data to txt file and figure to png --------------------------------------------------------------------------------------------------
# filename = "calibration - th1 - th2 - h" + str(heater) + " - " + str(temperature) + " K"
# np.savetxt(fname=filename + ".txt",
#            X=np.c_[iH,
#                    T1_avg, T1_std, T1_2w_0_avg, T1_2w_0_std, T1_2w_pi2_avg, T1_2w_pi2_std,
#                    T2_avg, T2_std, T2_2w_0_avg, T2_2w_0_std, T2_2w_pi2_avg, T2_2w_pi2_std],
#            header="Heater (mA), "
#                   "T1 (K), T1 std (K), T1_2w_0_avg (K), T1_2w_0_std (K), T1_2w_pi2_avg (K), T1_2w_pi2_std (K),"
#                   "T2 (K), T2 std (K), T2_2w_0_avg (K), T2_2w_0_std (K), T2_2w_pi2_avg (K), T2_2w_pi2_std (K)",
#            fmt=["%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f"],
#            delimiter=",", comments="", )
# fig.savefig(fname=filename + ".png", format="png", dpi=300)
#
# plt.show()
