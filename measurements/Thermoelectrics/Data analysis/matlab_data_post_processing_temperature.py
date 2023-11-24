from functions_import_mat_file import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import cm
import matplotlib


# USER SECTION - Select measurement conditions ---------------------------------------------------------------------------------------------
temperature = 300                               # select calibration bath temperature
heater = 1                                      # select either heater 1 or 2
avg_window = 60 * 1                             # set awg_window
subsampling = 500                              # set samples number of time plots


# Load files -------------------------------------------------------------------------------------------------------------------------------
th1_data = loadmat("calibration - th1 - h" + str(heater) + " - " + str(temperature) + " K.mat")             # load matlab file
th2_data = loadmat("calibration - th2 - h" + str(heater) + " - " + str(temperature) + " K.mat")             # load matlab file
th1_cal = np.genfromtxt(fname="calibration - th1 - " + str(temperature) + " K.txt", delimiter=",", skip_header=1)   # load calibration file
th2_cal = np.genfromtxt(fname="calibration - th2 - " + str(temperature) + " K.txt", delimiter=",", skip_header=1)   # load calibration file


# Check that the heater current steps are the same for the two thermometers ----------------------------------------------------------------
True if np.array_equal(th1_data["Lockin1"]["amplitude"], th2_data["Lockin1"]["amplitude"]) else exit("Heater current mismatch! Abort.")


# Get process parameters from files --------------------------------------------------------------------------------------------------------
th1_a0, th1_a1 = th1_cal[2], th1_cal[3]         # get Th1 slope and intercept
th2_a0, th2_a1 = th2_cal[2], th2_cal[3]         # get Th2 slope and intercept
iTh1 = th1_data["I_source"]["current1"] * 1E-6  # get Th1 DC current
iTh2 = th2_data["I_source"]["current2"] * 1E-6  # get Th2 DC current
iH = th1_data["Lockin1"]["amplitude"]           # get the heater current steps (always lockin1)
n = iH.shape[0]                                 # get the number of heater current steps (always lockin1, "-1" to exclude i = 0)
t1AC = th1_data["Gt"]["runtime_AC"]             # get Th1 time trace runtime, in seconds
t2AC = th2_data["Gt"]["runtime_AC"]             # get Th2 time trace runtime, in seconds


# Initialize figure ------------------------------------------------------------------------------------------------------------------------
fig = plt.figure(constrained_layout=False, figsize=(30/2.54, 20/2.54))  # create figure
gs = gridspec.GridSpec(ncols=3, nrows=3, figure=fig)                    # define grid spacing object
gs.update(wspace=0.4, hspace=0.4)                                       # set spacing between axes.
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_title("Thermometer 1")
ax1.set_xlabel("Time (min)")
ax1.set_ylabel(r"$\Theta$ (K)")
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_xlabel("Time (min)")
ax2.set_ylabel(r"$\Theta_{2\omega,0}$ (K)")
ax3 = fig.add_subplot(gs[2, 0])
ax3.set_ylabel(r"$\Theta_{2\omega,\pi/2}$ (K)")
ax3.set_xlabel("Time (min)")

ax4 = fig.add_subplot(gs[0, 1])
ax4.set_title("Thermometer 2")
ax4.set_xlabel("Time (min)")
ax4.set_ylabel(r"$\Theta$ (K)")
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_xlabel("Time (min)")
ax5.set_ylabel(r"$\Theta_{2\omega,0}$ (K)")
ax6 = fig.add_subplot(gs[2, 1])
ax6.set_ylabel(r"$\Theta_{2\omega,\pi/2}$ (K)")
ax6.set_xlabel("Time (min)")

ax7 = fig.add_subplot(gs[0, 2])
ax7.set_xlabel("Current (mA)")
ax7.set_ylabel(r"$\Theta_{avg}$ (K)")
ax8 = fig.add_subplot(gs[1, 2])
ax8.set_xlabel("Current (mA)")
ax8.set_ylabel(r"$\Delta\Theta_{2\omega,0}$ (K)")
ax9 = fig.add_subplot(gs[2, 2])
ax9.set_xlabel("Current (mA)")
ax9.set_ylabel(r"$\Delta\Theta_{2\omega,\pi/2}$ (K)")

c = cm.RdYlBu_r
norm = matplotlib.colors.Normalize(vmin=np.min(iH), vmax=np.max(iH))


# Initialize arrays ------------------------------------------------------------------------------------------------------------------------
T1_avg, T1_std = np.zeros(n), np.zeros(n)
T1_2w_0_avg, T1_2w_0_std = np.zeros(n), np.zeros(n)
T1_2w_pi2_avg, T1_2w_pi2_std = np.zeros(n), np.zeros(n)

T2_avg, T2_std = np.zeros(n), np.zeros(n)
T2_2w_0_avg, T2_2w_0_std = np.zeros(n), np.zeros(n)
T2_2w_pi2_avg, T2_2w_pi2_std = np.zeros(n), np.zeros(n)


# Read data, plot time traces and calculate averages ---------------------------------------------------------------------------------------
for i in range(0, n):  # replace 5 with index of AC temperature

    t1 = th1_data["Gt"]["time"][(th1_data["Gt"]["time"] < t1AC)]                     # get Th1 time
    nt1 = t1.shape[0]                                                                # get number of Th1 samples
    T1 = (th1_data["Gt"]["data_voltage"][5, i][4][0: nt1] / iTh1 - th1_a0) / th1_a1  # get Th1 DC temperature drift
    T1_2w_0 = th1_data["Gt"]["data_voltage"][5, i][0][0: nt1] / iTh1 / th1_a1        # get Th1 delta T at frequency 2w, in phase
    T1_2w_pi2 = - th1_data["Gt"]["data_voltage"][5, i][1][0: nt1] / iTh1 / th1_a1    # get Th1 delta T at frequency 2w, in quadrature

    t2 = th2_data["Gt"]["time"][(th2_data["Gt"]["time"] < t2AC)]                     # get Th2 time
    nt2 = t2.shape[0]                                                                # get number of Th2 samples
    T2 = (th2_data["Gt"]["data_voltage"][5, i][5][0: nt2] / iTh2 - th2_a0) / th2_a1  # get Th1 DC temperature drift
    T2_2w_0 = th2_data["Gt"]["data_voltage"][5, i][2][0: nt2] / iTh2 / th2_a1        # get Th1 delta T at frequency 2w, in phase
    T2_2w_pi2 = - th2_data["Gt"]["data_voltage"][5, i][3][0: nt2] / iTh2 / th2_a1    # get Th1 delta T at frequency 2w, in quadrature

    T1_avg[i] = np.mean(T1[t1 > np.max(t1) - avg_window])                       # calculate mean of Th1 dc temperature drift
    T1_std[i] = np.std(T1[t1 > np.max(t1) - avg_window])                        # calculate std dev of Th1 dc temperature drift
    T1_2w_0_avg[i] = np.mean(T1_2w_0[t1 > np.max(t1) - avg_window])             # calculate mean of Th1 2w_0 temperature amplitude
    T1_2w_0_std[i] = np.std(T1_2w_0[t1 > np.max(t1) - avg_window])              # calculate std dev of Th1 2w_0 temperature amplitude
    T1_2w_pi2_avg[i] = np.mean(T1_2w_pi2[t1 > np.max(t1) - avg_window])         # calculate mean of Th1 2w_pi2 temperature amplitude
    T1_2w_pi2_std[i] = np.std(T1_2w_pi2[t1 > np.max(t1) - avg_window])          # calculate std dev of Th1 2w_pi2 temperature amplitude

    T2_avg[i] = np.mean(T2[t2 > np.max(t2) - avg_window])                       # calculate mean of Th2 dc temperature drift
    T2_std[i] = np.std(T2[t2 > np.max(t2) - avg_window])                        # calculate std dev of Th2 dc temperature drift
    T2_2w_0_avg[i] = np.mean(T2_2w_0[t2 > np.max(t2) - avg_window])             # calculate mean of Th2 2w_0 temperature amplitude
    T2_2w_0_std[i] = np.std(T2_2w_0[t2 > np.max(t2) - avg_window])              # calculate std dev of Th2 2w_0 temperature amplitude
    T2_2w_pi2_avg[i] = np.mean(T2_2w_pi2[t2 > np.max(t2) - avg_window])         # calculate mean of Th2 2w_pi2 temperature amplitude
    T2_2w_pi2_std[i] = np.std(T2_2w_pi2[t2 > np.max(t2) - avg_window])          # calculate std dev of Th2 2w_pi2 temperature amplitude

    # Plot time traces
    rgba = c(norm(iH[i]))
    number_of_rows1 = t1.shape[0]
    random_indices1 = np.random.choice(number_of_rows1, size=subsampling, replace=False)
    number_of_rows2 = t2.shape[0]
    random_indices2 = np.random.choice(number_of_rows2, size=subsampling, replace=False)
    ax1.plot(t1[random_indices1] / 60, T1[random_indices1], marker="o", ms=4, linestyle="", alpha=0.1, c=rgba)
    ax2.plot(t1[random_indices1] / 60, T1_2w_0[random_indices1], marker="o", ms=4, linestyle="", alpha=0.1, c=rgba)
    ax3.plot(t1[random_indices1] / 60, T1_2w_pi2[random_indices1], marker="o", ms=4, linestyle="", alpha=0.1, c=rgba)
    ax4.plot(t2[random_indices2] / 60, T2[random_indices2], marker="o", ms=4, linestyle="", alpha=0.1, c=rgba)
    ax5.plot(t2[random_indices2] / 60, T2_2w_0[random_indices2], marker="o", ms=4, linestyle="", alpha=0.1, c=rgba)
    ax6.plot(t2[random_indices2] / 60, T2_2w_pi2[random_indices2], marker="o", ms=4, linestyle="", alpha=0.1, c=rgba)

    # Draw vertical lines where averaging begins
    ax1.axvline(x=np.max(t1) / 60 - avg_window / 60, linestyle="--", color="grey")
    ax2.axvline(x=np.max(t1) / 60 - avg_window / 60, linestyle="--", color="grey")
    ax3.axvline(x=np.max(t1) / 60 - avg_window / 60, linestyle="--", color="grey")
    ax4.axvline(x=np.max(t2) / 60 - avg_window / 60, linestyle="--", color="grey")
    ax5.axvline(x=np.max(t2) / 60 - avg_window / 60, linestyle="--", color="grey")
    ax6.axvline(x=np.max(t2) / 60 - avg_window / 60, linestyle="--", color="grey")

# Plot temperature drift and amplitudes against heater current
ax7.scatter(iH, (T1_avg + T2_avg) / 2, marker="o", c=c(norm(iH)))
ax8.scatter(iH, T1_2w_0_avg - T2_2w_0_avg, marker="o", c=c(norm(iH)))
ax9.scatter(iH, T1_2w_pi2_avg - T2_2w_pi2_avg, marker="o", c=c(norm(iH)))


# Save data to txt file and figure to png --------------------------------------------------------------------------------------------------
filename = "calibration - th1 - th2 - h" + str(heater) + " - " + str(temperature) + " K"
np.savetxt(fname=filename + ".txt",
           X=np.c_[iH,
                   T1_avg, T1_std, T1_2w_0_avg, T1_2w_0_std, T1_2w_pi2_avg, T1_2w_pi2_std,
                   T2_avg, T2_std, T2_2w_0_avg, T2_2w_0_std, T2_2w_pi2_avg, T2_2w_pi2_std],
           header="Heater (mA), "
                  "T1 (K), T1 std (K), T1_2w_0_avg (K), T1_2w_0_std (K), T1_2w_pi2_avg (K), T1_2w_pi2_std (K),"
                  "T2 (K), T2 std (K), T2_2w_0_avg (K), T2_2w_0_std (K), T2_2w_pi2_avg (K), T2_2w_pi2_std (K)",
           fmt=["%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f"],
           delimiter=",", comments="", )
fig.savefig(fname=filename + ".png", format="png", dpi=300)

plt.show()
