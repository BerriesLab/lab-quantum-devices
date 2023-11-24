# region ----- Import packages -----
import oxford_mercury_itc
import lakeshore_tc336
import mercuryitc
import pyvisa
import scipy.stats
import matplotlib.gridspec
import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os
import numpy as np
import time
import datetime
import pickle
# endregion

# region ----- USER inputs -----
# measurement(s) options ---------------------------------------------------------------------------------------------------------------------------------------
main = "E:/Samples"             # [string] main folder
chip = "test"                  # [string]: chip name
device = "10"                  # [string]: device string
t_start = 105                       # [float] initial temperature (in K) of the temperature sweep
t_stop = 100.4                    # [float] final temperature (in K) of the temperature sweep
t_step = 0.2                    # [float] temperature step (in K)
settling_time_t = 15 * 60       # [float] cryo stage thermalization time (in s)
settling_time_t_init = 15 * 60   # [float] initial cryo stage thermalization time (in s)
dt_lift = np.inf                    # [float] temperature interval in between needles lifting (in K)
# tc options ---------------------------------------------------------------------------------------------------------------------------------------------------
tc_model = 1                    # [string] select tc_model (0: lakeshore 336, 1: oxford mercury itc)
tc_address = "ASRL4::INSTR"         # [string] address of temperature controller
t_heater_range_switch = 50      # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium", above which is set to "high"
t_sampling_freq = 2             # [int] temperature sampling frequency (in Hz)
# endregion USER input

# region ----- Read resources and create instrumentation objects -----
print("\n***** Loading instrumentation drivers *****")
# Create a Resource Manager
rm = pyvisa.ResourceManager()
print(rm.list_resources())
if tc_model == 0:
    try:
        # define temperature controller visa object for Lakeshore 336
        tc = lakeshore_tc336.tc336(visa=rm.open_resource(tc_address))
        print("Found temperature controller: {}".format(tc.read_model()))
    except pyvisa.VisaIOError as e:
        raise pyvisa.VisaIOError("Cannot find temperature controller... Execution terminated.")
elif tc_model == 1:
    try:
        # define temperature controller visa object for Oxford Mercury ITC
        tc = oxford_mercury_itc.mercuryitc(rm.open_resource(tc_address))
        print("Found temperature controller: {}".format(tc.read_model))
    except pyvisa.VisaIOError as e:
        raise pyvisa.VisaIOError("Cannot find temperature controller... Execution terminated.")
else:
    raise ValueError("Temperature controller ID does not belong to the list of the accepted values.")
# endregion

# region ----- Make arrays of temperature, heater current and thermometer current -----
t_s = np.linspace(t_start, t_stop, int((abs(t_stop - t_start) / t_step + 1)), endpoint=True)
# endregion

# region ----- Set or create current directory where to save files -----
print("\n***** Measurement log *****")
path = main + "/" + chip + "/" + device + "/"
try:
    os.chdir(path)  # if path exists, then make it cwd
    print("{} ... found.".format(path))
except OSError:  # if path does not exists
    print("{} ... not found. Making directory... ".format(path))
    os.makedirs(path)  # make new directory
    os.chdir(path)  # make path cwd
print("Current working directory set to: {}".format(os.getcwd()))
# endregion

# region ----- Initialize figures -----
print("Initializing figure... ", end="")
plt.ion()
# -----
figtemp = plt.figure(figsize=(30 / 2.54, 20 / 2.54))
gridtemp = matplotlib.gridspec.GridSpec(nrows=1, ncols=1)
gridtemp.update(wspace=0.4, hspace=2)
# ------
axtemp = figtemp.add_subplot(gridtemp[0, 0])
axtemp.set_xlabel("Time (min)")
axtemp.set_ylabel("Temperature (K)")
axtemp.set_title("Temperature vs Time", fontsize=10, fontstyle="italic")
# ------
axtemp_legend = [Line2D([0], [0], color="orange", lw=4),
                 Line2D([0], [0], color="green", lw=4)]
axtemp.legend(axtemp_legend, ["Stage", "Shield"], loc="upper right")
# ------
c = matplotlib.cm.get_cmap("RdYlBu_r")
if t_stop >= t_start:
    norm = matplotlib.colors.Normalize(vmin=t_start, vmax=t_stop)
else:
    norm = matplotlib.colors.Normalize(vmin=t_stop, vmax=t_start)
plt.pause(0.001)
print("Done.")
# endregion

# set the temperature at which needles must be lifted and then lowered again before continuing
t_lift = t_start + dt_lift


for idx_t, t in enumerate(t_s):

    # region ----- Lift needles if needed -----
    if t > t_lift:  # check if needles must be lifted before proceeding
        input("Please ground the device, lift and then lower the probes back into position. Then unground the device and press Enter to continue...")
        t_lift = t + dt_lift  # update temperature lift value
    # endregion

    # region ----- Set temperature and wait for thermalization -----
    # set heater range
    if t >= t_heater_range_switch:
        if tc_model == 0:
            tc.set_heater_range(1, "high")
            tc.set_heater_range(2, "high")
    elif t < t_heater_range_switch:
        if tc_model == 0:
            tc.set_heater_range(1, "medium")
            tc.set_heater_range(2, "medium")
    # set stage and shield temperature
    if tc_model == 0:
        tc.set_temperature(output=1, t=t)
        tc.set_temperature(output=2, t=t)
    if tc_model == 1:
        tc.set_temperature(setpoint=t, output=0)
        tc.set_temperature(setpoint=40, output=1)
        time.sleep(5)
        tc.set_heater_percentage_auto(1)

    t0 = time.time()  # initialize initial time
    print("Waiting for thermalization at {:04.1f} K...".format(t), end="")
    if idx_t == 0:
        settling_time = settling_time_t_init
    else:
        settling_time = settling_time_t
    print(settling_time)
    # wait and plot temperature vs time
    axtemp.set_xlabel("Time (s)")
    axtemp.set_ylabel("Temperature (K)")
    axtemp.set_title("Temperature vs Time", fontsize=10, fontstyle="italic")
    axtemp_legend = [Line2D([0], [0], color="orange", lw=4),
                     Line2D([0], [0], color="green", lw=4)]
    axtemp.legend(axtemp_legend, ["Stage", "Shield"], loc="upper right")
    axtemp.set_xlim([0, settling_time])
    axtemp.axhline(y=t, linestyle="--")
    line1 = axtemp.plot(0, 0, lw=0, marker="o", markerfacecolor="orange", markeredgecolor="black", alpha=0.5)[0]
    # line2 = axtemp.plot(0, 0, lw=0, marker="o", markerfacecolor="green", markeredgecolor="black", alpha=0.5)[0]
    temp1 = np.zeros(int(np.ceil(settling_time * t_sampling_freq)))
    # temp2 = np.zeros(int(np.ceil(settling_time * t_sampling_freq)))
    tm = np.zeros(int(np.ceil(settling_time * t_sampling_freq)))
    idx_tm = 0
    while time.time() - t0 <= settling_time:
        if tc_model == 0:
            temps = tc.read_temperatures()
            axtemp.plot(time.time() - t0, temps[0], marker="o", markerfacecolor="orange", markeredgecolor="black", alpha=0.5)
            axtemp.plot(time.time() - t0, temps[1], marker="o", markerfacecolor="green", markeredgecolor="black", alpha=0.5)
            plt.pause(1)
        elif tc_model == 1:
            temp1[idx_tm] = tc.read_temperature("b")
            # temp2[idx_tm] = tc.read_temperature("he4pot")
            tm[idx_tm] = time.time() - t0
            line1.set_data(tm[:idx_tm], temp1[:idx_tm])
            # line2.set_data(tm[:idx_tm], temp2[:idx_tm])
            axtemp.relim()
            axtemp.autoscale_view(scaley=True, scalex=False)
            plt.pause(1 * t_sampling_freq)
        print(idx_tm)
        idx_tm = idx_tm + 1
    print("Done.")
    # endregion

    # region ----- Save temperature(s) vs time to disc -----
    if tc_model == 0:
        t_time = axtemp.lines[0].get_xdata()
        t_stage = axtemp.lines[0].get_ydata()
        t_shield = axtemp.lines[1].get_ydata()
    print("Saving file(s) to disc... ", end="")
    tm = np.trim_zeros(tm)
    temp1 = np.trim_zeros(temp1)
    # temp2 = np.trim_zeros(temp2)
    date = datetime.datetime.now()  # take a stamp of the measurement time
    filename = "{} - calibration t(time) - {:04.1f} K".format(date.strftime("%Y.%m.%d %H.%M.%S"), t)
    with open(filename + ".bin", "wb") as file:
        pickle.dump({"experiment": "calibration t(time)",
                     "chip": chip,
                     "device": device,
                     "date": date,
                     "settling time": settling_time_t,
                     "data": {"time": tm,
                              "t stage": temp1,
                              "t shield": None}, #temp2},
                     "settings": {"tc": tc.get_settings() if tc_model == 0 else None}
                     },
                    file)
    figtemp.savefig(fname=filename + ".png", format="png")
    print("Done.")
    # endregion

# region ----- Terminate program -----
input("Measurement complete. Ground the device then press Enter to terminate.")

# turn interactive mode off and plot
plt.ioff()
plt.show()
# endregion
