#######################################################################
#   Author:         Davide Beretta
#   Date:           09.04.2021
#   Description:    Interface 2x Keithley SMU 236
#                   for 3-terminal FET - Vg sweep - Synchronous
#######################################################################

# region ----- Import packages -----
import keithley_smu236
import pyvisa
import matplotlib.cm
import matplotlib.colors
import matplotlib.gridspec
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime
import pickle
# endregion

# region ----- USER inputs -----
# measurement(s) options -----------------------------------------------------------------------------------------------
main = "C:\\samples"                    # [string] Main folder directory
chip = "f005"                           # [string] chip name
device = "e"                            # [string] device name
channel_length = 8                      # [float] channel length (in um)
material = "PbS -EDT"                   # [string] material
environment = "air"                  # [string] measurement environment
illumination = "dark"                   # [string] illumination: "dark" or "light"
vgs = [0, 20, 0.1, "lin", 2]            # [list] Vgs (in V). In the order: start, stop, step size, lin-log, mode (0: single, 1: return, 2: hysteresis)
vds = np.array([10])                 # [array] Vds values (in V).
# smu gate options --------------------------------------------------------------------------------------------------
smu1_source_range = "auto"                 # [float] gate voltage source range
smu1_sense_range = 10e-9               # [float] current sense range
smu1_integration_time = 20e-3           # [float] integration time
smu1_samples = 0                        # [int] digital averaging
smu1_sensing = "local"                  # [string] "local" fro 2-wire, "remote" for 4-wire
smu1_address = "GPIB0::4::INSTR"        # [string] gate voltage source address
smu1_delay = 100                         # [float] time (in ms) between source and measure
smu1_delay_init = 10000                 # [float] time (in ms) between first source and measure
# smu vds options --------------------------------------------------------------------------------------------
smu2_source_range = "auto"                 # [float] gate voltage source range
smu2_sense_range = 10e-9               # [float] current sense range
smu2_integration_time = 20e-3           # [float] integration time
smu2_samples = 0                        # [int] digital averaging
smu2_sensing = "local"                 # [string] "local" fro 2-wire, "remote" for 4-wire
smu2_address = "GPIB0::5::INSTR"        # [string] gate voltage source address
smu2_delay = 100                        # [float] time (in ms) between source and measure. By default, the smu236 needs 100 ms to set a voltage.
smu2_delay_init = 10000                 # [float] time (in ms) between first source and measure
# endregion USER input

# region ----- Read resources and create instrumentation objects -----
print("\n***** Loading instrumentation drivers *****")
rm = pyvisa.ResourceManager()
try:
    # define voltage source object for device gate
    smu1 = keithley_smu236.smu236(visa=rm.open_resource(smu1_address))
    print("Found smu for Vgs: {}".format(smu1.read_model()))
except pyvisa.VisaIOError as e:
    exit("Cannot find smu for Vgs... Execution terminated.")
try:
    # define voltage source object for device bias
    smu2 = keithley_smu236.smu236(visa=rm.open_resource(smu2_address))
    print("Found smu for Vds : {}".format(smu2.read_model()))
except pyvisa.VisaIOError as e:
    exit("Cannot find smu for Vds... Execution terminated.")
# endregion

# region ----- Make arrays and inform the user -----
n_vds = len(vds)
n_vgs = int((vgs[1] - vgs[0]) / vgs[2] + 1)
if vgs[4] == 1:
    n_vgs = 2 * n_vgs - 1
if vgs[4] == 2:
    n_vgs = 4 * n_vgs - 3
n1 = smu1_samples if smu1_samples != 0 else 1
n2 = smu2_samples if smu2_samples != 0 else 1
default_delay1 = smu1.default_delay[smu1_sense_range]
default_delay2 = smu2.default_delay[smu2_sense_range]
print("\n"
      "***** {} - {} *****\n"
      "channel length: {}\n"
      "material: {}\n"
      "environment: {}\n"
      "illumination: {}\n".format(chip, device, channel_length, material, environment, illumination))
print("***** Vgs settings *****\n"
      "settling time: {} s\n"
      "delay: {} s\n"
      "integration time: {} s\n"
      "samples: {}\n".format(smu1_delay_init / 1000, smu1_delay / 1000, smu1_integration_time, smu1_samples))
print("***** Vgs settings *****\n"
      "delay: {} s\n"
      "integration time: {} s\n"
      "samples: {}\n".format(smu2_delay / 1000, smu2_integration_time, smu2_samples))
print("***** Measurement summary *****\n"
      "Vgs sweep from: {} V to: {} V with step: {} V, type: {} and mode: {}\n"
      "Vds values {}".format(vgs[0], vgs[1], vgs[2], vgs[3], vgs[4], vds))
if default_delay1 is not None and default_delay2 is not None:
    est_time = n_vds * (smu2_delay_init / 1000 + n_vgs * (default_delay1 + smu1_delay / 1000 + smu1_integration_time * n1 +
                                                          default_delay2 + smu2_delay / 1000 + smu2_integration_time * n2))
    print("Estimated measurement time: {:.1f} min.\n".format(est_time / 60))
else:
    est_time = n_vds * (smu2_delay_init / 1000 + n_vgs * (smu1_delay / 1000 + smu1_integration_time * n1 +
                                                          smu2_delay / 1000 + smu2_integration_time * n2))
    print("Cannot estimate measurement time because 'sense range' = 'auto'.\n"
          "Measurement time > {:.1f} min.\n".format(est_time / 60))
input("Press Enter to accept and proceed, press Ctrl-C to abort.")
# endregion

# region ----- Set or create current directory where to save files and allocate RAM -----
print("\n***** Measurement log *****")
path = main + "\\" + chip + "\\" + device + "\\3 terminal fet\\"
try:
    os.chdir(path)  # if path exists, then make it cwd
    print("{} ... found.".format(path))
except OSError:  # if path does not exists
    print("{} ... not found. Making directory... ".format(path), end="")
    os.makedirs(path)  # make new directory
    os.chdir(path)  # make path cwd
    print("Done.")
print("Current working directory set to: {}".format(os.getcwd()))
print("Allocating RAM... ", end="")
data = np.zeros((n_vgs, n_vds, 4))
print("Done.")
date = datetime.datetime.now()
file_name = "{} - 3 terminal fet vgs sweep.bin".format(date.strftime("%Y.%m.%d %H.%M.%S"))
file_backup_name = file_name + ".bak"
fig_name = "{} - 3 terminal fet vgs sweep.png".format(date.strftime("%Y.%m.%d %H.%M.%S"))
fig_backup_name = fig_name + ".bak"
# endregion

# region ----- Initialize figure -----
print("Initializing figure... ", end="")
plt.ion()
fig = plt.figure(figsize=(30 / 2.54, 15 / 2.54))
grid = matplotlib.gridspec.GridSpec(nrows=1, ncols=2)
fig.suptitle("Chip: {}. Device: {}.".format(chip, device), fontsize=12)
grid.update(wspace=0.4, hspace=2)
# ------------------------------------
ax1_lin = fig.add_subplot(grid[0, 0])  # Id vs Vg, linear scale
ax1_lin.set_xlabel("$V_{gs}$ (V)")
ax1_lin.set_ylabel("$I_{gs}$ (A)", color="orangered")
ax1_lin.tick_params(axis="y", colors="orangered")
# ------------------------------------
ax2_lin = ax1_lin.twinx()  # Ig vs Vg, linear scale
ax2_lin.set_ylabel("$I_{g}$ (A)", color="darkgreen")
ax2_lin.tick_params(axis="y", colors="darkgreen")
# ------------------------------------
ax3_log = fig.add_subplot(grid[0, 1])  # Ig, Id vs Vg, linear scale
ax3_log.set_xlabel("$V_{gs}$ (V)")
ax3_log.set_ylabel("$I$ (A)")
# ------------------------------------
cmap1 = matplotlib.cm.get_cmap("Oranges")
cmap2 = matplotlib.cm.get_cmap("Greens")
norm_vds = matplotlib.colors.Normalize(vmin=vds.min(), vmax=vds.max())
print("Done.")
# endregion

# region ----- Configure instrumentation -----
print("Configuring instrumentation... ", end="")
smu1.set_source("v")
smu1.set_function("sweep")
smu1.set_sense_range(smu1_sense_range)
smu1.set_filter(smu1_samples)
smu1.set_integration_time(smu1_integration_time)
smu1.set_sensing(smu1_sensing)
smu1.set_srq_mask("sweep done")
smu1.set_trigger_off()
smu1.set_trigger_control("external", "^src dly msr", "src dly msr^", "disabled")
smu1.set_trigger_on()
smu2.set_source("v")
smu2.set_function("sweep")
smu2.set_sense_range(smu2_sense_range)
smu2.set_filter(smu2_samples)
smu2.set_integration_time(smu2_integration_time)
smu2.set_sensing(smu2_sensing)
smu2.set_srq_mask("sweep done")
smu2.set_trigger_off()
smu2.set_trigger_control("external", "^src dly msr", "src dly msr^", "enabled")
smu2.set_trigger_on()
print("Done.")
# endregion

print("Switching on instrumentation... ", end="")
smu1.switch_on()
smu2.switch_on()
print("Done.")

for idx, val in enumerate(vds):

    print("Making Vgs sweep at Vds = {} ... ".format(val), end="")

    smu2.create_fixed_staircase(val, smu2_source_range, smu2_delay_init, 1)
    smu2.append_fixed_staircase(val, smu2_source_range, smu2_delay, n_vgs-1)

    if vgs[3] == "lin":
        if vgs[4] == 0:
            smu1.create_linear_staircase(vgs[0], vgs[1], vgs[2], smu1_source_range, smu1_delay)
        if vgs[4] == 1:
            smu1.create_linear_staircase(vgs[0], vgs[1], vgs[2], smu1_source_range, smu1_delay)
            smu1.append_linear_staircase(vgs[1] - vgs[2], vgs[0], vgs[2], smu1_source_range, smu1_delay)
        if vgs[4] == 2:
            smu1.create_linear_staircase(vgs[0], vgs[1], vgs[2], smu1_source_range, smu1_delay)
            smu1.append_linear_staircase(vgs[1] - vgs[2], vgs[1] - 2 * (vgs[1] - vgs[0]), vgs[2], smu1_source_range, smu1_delay)
            smu1.append_linear_staircase(vgs[1] - 2 * (vgs[1] - vgs[0]) + vgs[2], vgs[0], vgs[2], smu1_source_range, smu1_delay)
    if vgs[3] == "log":
        print("Not yet implemented")
        if vgs[4] == 0:
            smu1.create_logarithmic_staircase(vgs[0], vgs[1], vgs[2], smu1_source_range, smu1_delay)
        if vgs[4] == 1:
            smu1.create_logarithmic_staircase(vgs[0], vgs[1], vgs[2], smu1_source_range, smu1_delay)
            smu1.append_logarithmic_staircase(vgs[1], vgs[0], vgs[2], smu1_source_range, smu1_delay)
        if vgs[4] == 2:
            smu1.create_logarithmic_staircase(vgs[0], vgs[1], vgs[2], smu1_source_range, smu1_delay)
            smu1.append_logarithmic_staircase(vgs[1], vgs[1] - 2 * (vgs[1] - vgs[0]), vgs[2], smu1_source_range, smu1_delay)
            smu1.append_logarithmic_staircase(vgs[1] - 2 * (vgs[1] - vgs[0]), vgs[0], vgs[2], smu1_source_range, smu1_delay)

    smu2.send_trigger()
    smu2.wait_for_srq()
    smu1.wait_for_srq()
    data[:, idx, 2], data[:, idx, 3] = smu1.read_buffer()
    data[:, idx, 0], data[:, idx, 1] = smu2.read_buffer()
    print("Done.")

    # region ----- Update figure -----
    print("Updating figure... ", end="")
    ax1_lin.plot(data[:, idx, 2], data[:, idx, 1], linewidth=0, marker="o", markeredgecolor="black", markerfacecolor=cmap1(norm_vds(val)) if len(vds) > 1 else "orange", alpha=0.4)
    ax2_lin.plot(data[:, idx, 2], data[:, idx, 3], linewidth=0, marker="D", markeredgecolor="black", markerfacecolor=cmap2(norm_vds(val)) if len(vds) > 1 else "green", alpha=0.4)
    ax3_log.semilogy(data[:, idx, 2], abs(data[:, idx, 1]), linewidth=0, marker="o", markeredgecolor="black", markerfacecolor=cmap1(norm_vds(val)) if len(vds) > 1 else "orange", alpha=0.4)
    ax3_log.semilogy(data[:, idx, 2], abs(data[:, idx, 3]), linewidth=0, marker="D", markeredgecolor="black", markerfacecolor=cmap2(norm_vds(val)) if len(vds) > 1 else "green", alpha=0.4)
    plt.pause(0.0001)
    print("Done.")
    # endregion

    # region ----- Save data and figure to disc -----
    print("Saving data to disc... ", end="")
    if os.path.exists(file_name):
        if os.path.exists(file_backup_name):
            os.remove(file_backup_name)
        os.rename(file_name, file_backup_name)
    with open(file_name, "wb") as file:
        pickle.dump({"date": date,
                     "chip": chip,
                     "device": device,
                     "channel length": channel_length,
                     "experiment": "3 terminal fet vgs sweep",
                     "environment": environment,
                     "illumination": illumination,
                     "material": material,
                     "data": data,
                     "settings": {"smu vds": smu2.get_settings(),
                                  "smu vds delay initial": smu2_delay_init,
                                  "smu vds delay": smu2_delay,
                                  "smu vgs": smu1.get_settings(),
                                  "smu vgs delay initial": smu1_delay_init,
                                  "smu vgs delay": smu1_delay},
                     },
                    file)
    if os.path.exists(fig_name):
        if os.path.exists(fig_backup_name):
            os.remove(fig_backup_name)
        os.rename(fig_name, fig_backup_name)
    plt.savefig(fname=fig_name, format="png")
    print("Done.")
    # endregion

print("Switching off instrumentation... ", end="")
smu1.set_bias_level(bias=0, delay=0)
smu1.switch_off()
smu2.set_bias_level(bias=0, delay=0)
smu2.switch_off()
print("Done.")

if os.path.exists(file_backup_name):
    os.remove(file_backup_name)
if os.path.exists(fig_backup_name):
    os.remove(fig_backup_name)

print("Measurement completed.")

plt.ioff()
plt.show()
