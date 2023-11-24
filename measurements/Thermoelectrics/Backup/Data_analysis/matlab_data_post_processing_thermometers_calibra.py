from functions_import_mat_file import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import cm
import matplotlib
import scipy.stats as stats


# USER - Select measurement conditions -----------------------------------------------------------------------------------------------------
thermometer = 2                                 # select either thermometer 1 or 2
temperature = 300                               # select calibration bath temperature
heater = 1                                      # select either heater 1 or 2
avg_window = 60 * 10                            # set averaging time window

# Check on user entries
exit("Thermometer does not exist") if (thermometer != 1) and (thermometer != 2) else True
exit("Heater does not exist") if (heater != 1) and (heater != 2) else True
# exit("Temperature") if temperature not in [0, 450] else True

# Load mat file ----------------------------------------------------------------------------------------------------------------------------
filename = "calibration - th" + str(thermometer) + " - h" + str(heater) + " - " + str(temperature) + " K"
data = loadmat(filename + ".mat")               # load mat file


# Get process parameters from files --------------------------------------------------------------------------------------------------------
n = data["Settings"]["temperatureDC"].size              # get the number of temperature steps
idx = 4 if thermometer == 1 else 5                      # set ADWin input index
iTh = data["I_source"]["current1"] * 1E-6 if thermometer == 1 else data["I_source"]["current2"] * 1E-6  # set thermometer current


# Initialize figure ------------------------------------------------------------------------------------------------------------------------
fig = plt.figure(constrained_layout=False, figsize=(30/2.54, 15/2.54))              # create figure
gs = gridspec.GridSpec(ncols=3, nrows=2, figure=fig)    # define grid spacing object
gs.update(wspace=0.4, hspace=0.3)                       # set the spacing between axes.
ax1 = fig.add_subplot(gs[:, 0])
ax1.set_xlabel("Time (min)")
ax1.set_ylabel("Temperature (K)")
ax2 = fig.add_subplot(gs[:, 1])
ax2.set_xlabel("Time (min)")
ax2.set_ylabel(r"Resistance ($\Omega$)")
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_xlabel("Temperature (K)")
ax3.set_ylabel(r"Resistance ($\Omega$)")
ax4 = fig.add_subplot(gs[1, 2])
ax4.set_xlabel("Temperature (K)")
ax4.set_ylabel(r"Residuals ($\Omega$)")
c = cm.RdYlBu_r
norm = matplotlib.colors.Normalize(vmin=np.min(data["Settings"]["temperatureDC"]), vmax=np.max(data["Settings"]["temperatureDC"]))


# Initialize arrays ------------------------------------------------------------------------------------------------------------------------
T_stage_avg, T_stage_std = np.zeros(n), np.zeros(n)
R_avg, R_std = np.zeros(n), np.zeros(n)


# Read data, plot time traces and calculate averages ---------------------------------------------------------------------------------------
for i in range(0, n):

    tT = data["Gt"]["temperature"][i, 0][:, 0]          # get time for temperature signals
    tV = data["Gt"]["time"]                             # get time for voltage signals
    T_stage = data["Gt"]["temperature"][i, 0][:, 1]     # get stage temperature array
    R = data["Gt"]["data_voltage"][i, 0][idx]/iTh       # get Th1 DC resistance

    T_stage_avg[i] = np.mean(T_stage[tT > np.max(tT) - avg_window])     # calculate mean of stage temperature
    T_stage_std[i] = np.mean(T_stage[tT > np.max(tT) - avg_window])     # calculate std dev of stage temperature

    R_avg[i] = np.mean(R[tV > np.max(tV) - avg_window])                 # calculate mean of resistance
    R_std[i] = np.mean(R[tV > np.max(tV) - avg_window])                 # calculate std dev of resistance

    number_of_rows = tT.shape[0]
    random_indices = np.random.choice(number_of_rows, size=500, replace=False)
    rgba = c(norm(T_stage_avg[i]))
    ax1.plot(tT[random_indices]/60, T_stage[random_indices], marker="o", ms=4, linestyle="", alpha=0.1, c=rgba)
    ax1.axvline(x=np.max(tT)/60 - avg_window/60, linestyle="--", color="grey")

    number_of_rows = tV.shape[0]
    random_indices = np.random.choice(number_of_rows, size=500, replace=False)
    ax2.plot(tV[random_indices]/60, R[random_indices], marker="o", ms=4, linestyle="", alpha=0.1, c=rgba)
    ax2.axvline(x=np.max(tV)/60 - avg_window/60, linestyle="--", color="grey")
    ax2.plot([np.max(tV)/60 - avg_window/60, np.max(tV)/60], [R_avg[i], R_avg[i]], c=rgba, linewidth=3, linestyle="--")

ax3.scatter(T_stage_avg, R_avg, marker="o", c=c(norm(T_stage_avg)))
slope, intercept, rvalue, pvalue, stderr = stats.linregress(T_stage_avg, R_avg)  # linear fit
ax3.plot(T_stage_avg, intercept + slope * T_stage_avg, marker="", linestyle="--", alpha=1, color="red")
text = "a0 = " + "{:.3f}".format(intercept) + r" $\Omega$" + "\n" + "a1 = " + "{:.3f}".format(slope) + r" $\Omega$/K" + "\n"
ax3.text(0.1, 0.7, text, transform=ax3.transAxes)

ax4.scatter(T_stage_avg, intercept + slope * T_stage_avg - R_avg, marker="o", c=c(norm(T_stage_avg)))
ax4.fill_between(T_stage_avg, 0, intercept + slope * T_stage_avg - R_avg, facecolor="black", alpha="0.2")


# Save data and figure ---------------------------------------------------------------------------------------------------------------------
filename = "calibration - th" + str(thermometer) + " - " + str(temperature) + " K"
np.savetxt(fname=filename + ".txt", X=np.c_[thermometer, temperature, intercept, slope, rvalue, pvalue, stderr],
           header="Thermometer, Temperature (K), a0 (Omega), a1 (Omega/K), r value, p value, std err",
           delimiter=",", comments="", fmt=["%d", "%d", "%.6f", "%.6f", "%.6f", "%.6f", "%.6f"])
fig.savefig(fname=filename + ".png", format="png", dpi=300)
plt.show()
