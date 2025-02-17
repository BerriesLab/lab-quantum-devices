# region ----- Import packages -----
import keithley_smu236
import pyvisa
from Objects.measurement import *
import os
from numpy import linspace, savetxt, floor, log10, ceil, log
import time
import datetime
import pickle

# endregion

"""
#######################################################################
    Author:         Davide Beretta
    Date:           06.01.2022
    Description:    FET

    This script can make: 
    (1) Transfer characteristic: Ids vs Vgs sweep at constant Vds
    (2) Output characteristic: Ids vs Vds sweep at constant Vgs
    (3) IV: Ids vs Vds sweep with floating gate
#######################################################################
"""

# region ----- USER inputs -----
sweep = 2  # [int] select between "Transfer characteristic" (0), "Output characteristic" (1), and "IV" (2)
sweepd = {0: "transfer characteristic", 1: "output characteristic", 2: "iv"}
# measurement(s) options -----------------------------------------------------------------------------------------------
experiment = Experiment()
experiment.experiment_name = f"{sweepd[sweep]}"
experiment.main_path = r"C:\samples\dabe\annealed"
experiment.date = datetime.datetime.now()
experiment.architecture = "tetra_te_00"  # Select from Chip folder
experiment.chip = "tep_ch1_10"
experiment.device = "a1"
experiment.filename = f"{experiment.date.strftime('%Y.%m.%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment_name}.data"
experiment.backup_filename = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
vgs = [0, 0, 1, "lin", 0, 1]  # [list] Vgs (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
vds = [0, 10e-3, 21, "lin", 1, 1]  # [list] Vds (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
fet = FET.Sweep(vgs, vds)  # ---------------------------------------------------------------------
fet.environment = 0  # [int] measurement environment {0: vacuum, 1: air, 2: N2, 3: Ar}
fet.illumination = 0  # [int] illumination {0: dark, 1: light}
fet.annealing = 0  # [int] {0: not annealed, 1: annealed}
fet.temperature = 273.15 + 25  # [float] temperature (in K)
fet.comment = ""
# endregion

# region ----- settings ------
settings = EmptyClass()
# ----- smu gate settings -----
settings.__setattr__("smu_vgs", EmptyClass())
settings.smu_vgs.model = 0  # [int] select tc model (0: keithley 236)
settings.smu_vgs.address = "GPIB0::1::INSTR"  # "ASRL8::INSTR"        # [string] address of temperature controller
settings.smu_vgs.source_range = 110  # [float] gate voltage source range
settings.smu_vgs.sense_range = 100e-9  # [float] current sense range
settings.smu_vgs.compliance = 1e-6  # [float] voltage compliance
settings.smu_vgs.integration_time = 20e-3  # [float] integration time
settings.smu_vgs.samples = 0  # [int] digital averaging
settings.smu_vgs.sensing = "local"  # [string] "local" fro 2-wire, "remote" for 4-wire
settings.smu_vgs.delay = 0.001  # [float] time (in s) between source and measure
settings.smu_vgs.delay_init = 0  # [float] time (in s) between source and measure
settings.smu_vgs.ramp_step = 100e-3  # [float] gate sweep step size (in V) (when sweeping Vds)
settings.smu_vgs.ramp_delay = 10e-3  # [float] gate sweep step size (in V) (when sweeping Vds)
# -------------------------------------------------------------------------------------------------
settings.__setattr__("smu_vds", EmptyClass())
settings.smu_vds.model = 0  # [int] select tc model (0: keithley 236)
settings.smu_vds.address = "GPIB0::2::INSTR"  # [string] gate voltage source address
settings.smu_vds.source_range = 1.1  # [float] gate voltage source range
settings.smu_vds.sense_range = 100e-6  # [float] current sense range
settings.smu_vds.compliance = 1e-3  # [float] voltage compliance
settings.smu_vds.integration_time = 20e-3  # [float] integration time
settings.smu_vds.samples = 0  # [int] digital averaging
settings.smu_vds.sensing = "local"  # [string] "local" fro 2-wire, "remote" for 4-wire
settings.smu_vds.delay = 0.001  # [float] time (in s) between source and measure
settings.smu_vds.delay_init = 0  # [float] time (in s) between source and measure
settings.smu_vds.ramp_step = 100e-3  # [float] drain-source sweep step size (in V) (when sweeping Vgs)
settings.smu_vds.ramp_delay = 10e-3  # [float] drain-source sweep step size (in V) (when sweeping Vgs)
# -------------------------------------------------------------------------------------------------
experiment.settings = settings
# endregion

# region ----- Read resources and create instrumentation objects -----
print("Listing instrumentation... ")
rm = pyvisa.ResourceManager()
try:
    # define voltage source object for device gate
    smu_vgs = keithley_smu236.smu236(visa=rm.open_resource(settings.smu_vgs.address))
    print("Found smu for gating: {}".format(smu_vgs.read_model()))
except pyvisa.VisaIOError as e:
    exit("Cannot find smu for gating... Execution terminated.")
try:
    # define voltage source object for device bias
    smu_vds = keithley_smu236.smu236(visa=rm.open_resource(settings.smu_vds.address))
    print("Found smu for Vds biasing: {}".format(smu_vds.read_model()))
except pyvisa.VisaIOError as e:
    exit("Cannot find smu Vds biasing... Execution terminated.")
# endregion

# region ----- Configure instrumentation -----
if sweep == 0 or sweep == 1:
    smu_vgs.bias("v", 0, settings.smu_vgs.source_range, settings.smu_vgs.sense_range, settings.smu_vgs.delay,
                 settings.smu_vgs.samples, settings.smu_vgs.integration_time, settings.smu_vgs.sensing,
                 settings.smu_vgs.compliance)
smu_vds.bias("v", 0, settings.smu_vds.source_range, settings.smu_vds.sense_range, settings.smu_vds.delay,
             settings.smu_vds.samples, settings.smu_vds.integration_time, settings.smu_vds.sensing,
             settings.smu_vds.compliance)
# endregion

# region ----- Message to the user -----
if settings.smu_vds.sense_range != "auto":
    vds_default_delay = smu_vds.default_delay[settings.smu_vds.sense_range]
else:  # else: select best case and inform user it might be longer
    vds_default_delay = 0
if settings.smu_vgs.sense_range != "auto":
    vgs_default_delay = smu_vgs.default_delay[settings.smu_vgs.sense_range]
else:  # else: select best case and inform user it might be longer
    vgs_default_delay = 0e-3
exp_dict = {0: "Vgs Sweep", 1: "Vds Sweep", 2: "IV"}
print(f"""\n***** measurement summary *****
chip: {experiment.chip}
device: {experiment.device}
experiment: {exp_dict[sweep]}
temperatures: {fet.temperature:.1f}""")
input(
    f"Vds total delay time: {'> ' if settings.smu_vds.sense_range == 'auto' else ''}{(vds_default_delay + settings.smu_vds.delay) * 1e3:.0f} ms\n"
    f"Vgs total delay time: {'> ' if settings.smu_vgs.sense_range == 'auto' else ''}{(vgs_default_delay + settings.smu_vgs.delay) * 1e3:.0f} ms\n"
    f"Press Enter to accept and proceed, press Ctrl-C to abort.")
# endregion

# region ----- Set or create current directory where to save files -----
print("\n***** measurement log *****")
subdir = {0: 'vgs sweep', 1: 'vds sweep', 2: "iv"}
path = rf"{experiment.main_path}\{experiment.chip}\{experiment.device}\{subdir[sweep]}"
try:
    os.chdir(path)  # if path exists, then make it cwd
    print(f"{path} ... found.")
except OSError:  # if path does not exists
    print(f"{path} ... not found. Making directory... ")
    os.makedirs(path)  # make new directory
    os.chdir(path)  # make path cwd
print(f"Current working directory set to: {os.getcwd()}")
# endregion

# region ----- Initialize figure -----
print("Initializing figure... ", end="")
if sweep == 0:
    plot1 = FET.PlotTransferCharacteristic(fet.vgs, fet.vds)
elif sweep == 1:
    plot1 = FET.PlotOutputCharacteristic(fet.vgs, fet.vds)
elif sweep == 2:
    plot1 = FET.PlotIV(fet.vds)
fig_name = f"{experiment.filename[:-5]}.png"
fig_backup_name = fig_name + ".bak"
print("Done.")  # endregion

if sweep == 0:

    t0 = datetime.datetime.now().timestamp()

    for i in range(len(fet.vds)):

        # region ----- Set vds -----
        print(f"Setting Vds to {fet.vds[i]:.3f} V... ", end="")
        if i == 0 and fet.vds[0] == 0:
            pass
        elif i == 0 and fet.vds[0] != 0:
            for x in linspace(0, fet.vds[i], int(ceil(abs(fet.vds[i]) / settings.smu_vds.ramp_step) + 1)):
                smu_vds.set_bias_level(bias=x, delay=settings.smu_vds.ramp_delay)
        else:
            for x in linspace(fet.vds[i - 1], fet.vds[i], int(ceil(abs(fet.vds[i] - fet.vds[i - 1]) / settings.smu_vds.ramp_step) + 1)):
                smu_vds.set_bias_level(bias=x, delay=settings.smu_vds.ramp_delay)
        print("Done.")
        # endregion

        # region ----- Wait for steady state -----
        t0 = time.time()
        while time.time() - t0 <= settings.smu_vds.delay_init:
            plt.pause(0.001)
            continue
        # endregion

        # region ----- Measure and plot in real time -----
        print("Measuring... ", end="")
        for j in range(len(fet.vgs)):

            # region ----- Set vgs -----
            if i == 0 and j == 0 and fet.vgs[0] != 0:
                for x in linspace(0, fet.vgs[j], int(abs(fet.vgs[j] - 0) / settings.smu_vgs.ramp_step) + 1):
                    smu_vgs.set_bias_level(bias=x, delay=settings.smu_vgs.ramp_delay)
                # region ----- Wait for steady state -----
                dt = time.time()
                while time.time() - dt <= settings.smu_vgs.delay_init:
                    plt.pause(0.001)
                    continue
                # endregion
            elif i > 0 and j == 0 and fet.vgs[0] != fet.vgs[-1]:
                for x in linspace(fet.vgs[-1], fet.vgs[0],
                                  int(abs(fet.vgs[-1] - fet.vgs[0]) / settings.smu_vgs.ramp_step) + 1):
                    smu_vgs.set_bias_level(bias=x, delay=settings.smu_vgs.ramp_delay)
                # region ----- Wait for steady state -----
                dt = time.time()
                while time.time() - dt <= settings.smu_vgs.delay_init:
                    plt.pause(0.001)
                    continue
                # endregion
            else:
                smu_vgs.set_bias_level(bias=fet.vgs[j], delay=settings.smu_vgs.delay)
            # endregion

            # region ----- Get data -----
            fet.data[j, i, 0], fet.data[j, i, 1] = smu_vgs.read()  # return source, measure
            fet.data[j, i, 2], fet.data[j, i, 3] = smu_vds.read()  # return source, measure
            fet.data[j, i, 4] = floor(j / (len(fet.vgs) / vgs[5]))  # store number of iteration, starting from 0
            fet.data[j, i, 5] = floor(i / (len(fet.vds) / vds[5]))  # store number of iteration, starting from 0
            fet.data[j, i, 6] = datetime.datetime.now().timestamp() - t0  # store datetime
            # endregion

            # region ----- Update figure -----
            plot1.ax0.lines[2 * i + 0].set_data(fet.data[0: j + 1, i, 0], fet.data[0: j + 1, i, 1])
            plot1.ax0.lines[2 * i + 1].set_data(fet.data[0: j + 1, i, 0], fet.data[0: j + 1, i, 3])
            plot1.ax0.relim()
            plot1.ax0.autoscale_view(scalex=False, scaley=True)
            plot1.ax1.lines[2 * i + 0].set_data(fet.data[0: j + 1, i, 0], log10(abs(fet.data[0: j + 1, i, 1])))
            plot1.ax1.lines[2 * i + 1].set_data(fet.data[0: j + 1, i, 0], log10(abs(fet.data[0: j + 1, i, 3])))
            plot1.ax1.relim()
            plot1.ax1.autoscale_view(scalex=False, scaley=True)
            plt.pause(1e-3)
            # endregion

        print("Done.")  # endregion

        # region ----- Save data and figure to disc -----
        print("Saving data to disc...", end="")
        experiment.data = fet
        if os.path.exists(experiment.filename):
            if os.path.exists(experiment.backup_filename):
                os.remove(experiment.backup_filename)
            os.rename(experiment.filename, experiment.backup_filename)
        with open(experiment.filename, "wb") as file:
            pickle.dump(experiment, file)

        if os.path.exists(fig_name):
            if os.path.exists(fig_backup_name):
                os.remove(fig_backup_name)
            os.rename(fig_name, fig_backup_name)
        plt.savefig(fname=fig_name, format="png")

        if os.path.exists(experiment.filename[:-4] + "txt"):
            if os.path.exists(experiment.backup_filename[:-8] + "txt.bak"):
                os.remove(experiment.backup_filename[:-8] + "txt.bak")
            os.rename(experiment.filename[:-4] + "txt", experiment.backup_filename[:-8] + "txt.bak")
        txt = []
        for k in range(fet.data.shape[1]):
            for q in range(fet.data.shape[0]):
                txt.append(fet.data[q, k, :])
        savetxt(experiment.filename[:-4] + "txt", txt, delimiter=",", newline='\n', header="vgs,igs,vds,ids,cycle,time",
                comments="# "+fet.comment+"\n", footer='', encoding=None)
        print("Done.")  # endregion

    # region ----- Set Vds to 0 V -----
    print("Sweeping Vds from {} V to 0 V... ".format(fet.vds[-1]), end="")
    for x in linspace(fet.vds[-1], 0, int(ceil(abs(fet.vds[-1]) / settings.smu_vds.ramp_step) + 1)):
        smu_vds.set_bias_level(bias=x, delay=settings.smu_vds.ramp_delay)
    print("Done.")  # endregion

    # region ----- Set Vgs to 0 V -----
    print("Sweeping Vgs from {} V to 0 V... ".format(fet.vgs[-1]), end="")
    for x in linspace(fet.vgs[-1], 0, int(ceil(abs(fet.vgs[-1]) / settings.smu_vgs.ramp_step) + 1)):
        smu_vgs.set_bias_level(bias=x, delay=settings.smu_vgs.ramp_delay)
    print("Done.")  # endregion

if sweep == 1:

    t0 = datetime.datetime.now().timestamp()

    for i in range(len(fet.vgs)):

        # region ----- Set vgs -----
        print(f"Setting Vgs to {fet.vgs[i]:.3f} V... ", end="")
        if i == 0 and fet.vgs[0] == 0:
            pass
        elif i == 0 and fet.vgs[0] != 0:
            for x in linspace(0, fet.vgs[i], int(ceil(abs(fet.vgs[i]) / settings.smu_vgs.ramp_step) + 1)):
                smu_vgs.set_bias_level(bias=x, delay=settings.smu_vgs.ramp_delay)
        else:
            for x in linspace(fet.vgs[i - 1], fet.vgs[i], int(ceil(abs(fet.vgs[i] - fet.vgs[i - 1]) / settings.smu_vgs.ramp_step) + 1)):
                smu_vgs.set_bias_level(bias=x, delay=settings.smu_vgs.ramp_delay)
        print("Done.")
        # endregion

        # region ----- Wait for steady state -----
        t0 = time.time()
        while time.time() - t0 <= settings.smu_vgs.delay_init:
            plt.pause(0.001)
            continue
        # endregion

        # region ----- Measure and plot in real time -----
        print("Measuring... ", end="")
        for j in range(len(fet.vds)):

            # region ----- Set vds -----
            if i == 0 and j == 0 and fet.vds[0] != 0:
                for x in linspace(0, fet.vds[j], int(abs(fet.vds[j] - 0) / settings.smu_vds.ramp_step) + 1):
                    smu_vds.set_bias_level(bias=x, delay=settings.smu_vds.ramp_delay)
                # region ----- Wait for steady state -----
                dt = time.time()
                while time.time() - dt <= settings.smu_vds.delay_init:
                    plt.pause(0.001)
                    continue
                # endregion
            elif i > 0 and j == 0 and fet.vds[0] != fet.vds[-1]:
                for x in linspace(fet.vds[-1], fet.vds[0],
                                  int(abs(fet.vds[-1] - fet.vds[0]) / settings.smu_vds.ramp_step) + 1):
                    smu_vds.set_bias_level(bias=x, delay=settings.smu_vds.ramp_delay)
                # region ----- Wait for steady state -----
                dt = time.time()
                while time.time() - dt <= settings.smu_vds.delay_init:
                    plt.pause(0.001)
                    continue
                # endregion
            else:
                smu_vds.set_bias_level(bias=fet.vds[j], delay=settings.smu_vds.delay)
            # endregion

            # region ----- Get data -----
            if sweep == 1:
                fet.data[i, j, 0], fet.data[i, j, 1] = smu_vgs.read()  # return source, measure
            fet.data[i, j, 2], fet.data[i, j, 3] = smu_vds.read()  # return source, measure
            fet.data[i, j, 4] = floor(i / (len(fet.vgs) / vgs[5]))  # store number of vgs iteration, starting from 0
            fet.data[i, j, 5] = floor(j / (len(fet.vds) / vds[5]))  # store number of vds iteration, starting from 0
            fet.data[i, j, 6] = datetime.datetime.now().timestamp() - t0  # store datetime
            # endregion

            # region ----- Update figure -----
            if sweep == 1:
                plot1.ax0.lines[2 * i + 0].set_data(fet.data[i, 0: j + 1, 2], fet.data[i, 0: j + 1, 1])
            plot1.ax0.lines[2 * i + 1].set_data(fet.data[i, 0: j + 1, 2], fet.data[i, 0: j + 1, 3])
            plot1.ax0.relim()
            plot1.ax0.autoscale_view(scalex=False, scaley=True)
            if sweep == 1:
                plot1.ax1.lines[2 * i + 0].set_data(fet.data[i, 0: j + 1, 2], log10(abs(fet.data[i, 0: j + 1, 1])))
            plot1.ax1.lines[2 * i + 1].set_data(fet.data[i, 0: j + 1, 2], log10(abs(fet.data[i, 0: j + 1, 3])))
            plot1.ax1.relim()
            plot1.ax1.autoscale_view(scalex=False, scaley=True)
            plt.pause(1e-3)
            # endregion

        print("Done.")  # endregion

        # region ----- Save data and figure to disc -----
        print("Saving data to disc...", end="")
        experiment.data = fet
        if os.path.exists(experiment.filename):
            if os.path.exists(experiment.backup_filename):
                os.remove(experiment.backup_filename)
            os.rename(experiment.filename, experiment.backup_filename)
        with open(experiment.filename, "wb") as file:
            pickle.dump(experiment, file)

        if os.path.exists(fig_name):
            if os.path.exists(fig_backup_name):
                os.remove(fig_backup_name)
            os.rename(fig_name, fig_backup_name)
        plt.savefig(fname=fig_name, format="png")

        if os.path.exists(experiment.filename[:-4] + "txt"):
            if os.path.exists(experiment.backup_filename[:-8] + "txt.bak"):
                os.remove(experiment.backup_filename[:-8] + "txt.bak")
            os.rename(experiment.filename[:-4] + "txt", experiment.backup_filename[:-8] + "txt.bak")
        txt = []
        for k in range(fet.data.shape[1]):
            for q in range(fet.data.shape[0]):
                txt.append(fet.data[q, k, :])
        savetxt(experiment.filename[:-4] + "txt", txt, delimiter=",", newline='\n',
                header="vgs,igs,vds,ids,vgs cycle,vds cycle, time", comments="# "+fet.comment+"\n", footer='', encoding=None)
        print("Done.")  # endregion

    # region ----- Set Vds to 0 V -----
    print(f"Sweeping Vds from {fet.vds[-1]:.3f} V to 0 V... ", end="")
    for x in linspace(fet.vds[-1], 0, int(ceil(abs(fet.vds[-1]) / settings.smu_vds.ramp_step) + 1)):
        smu_vds.set_bias_level(bias=x, delay=settings.smu_vds.delay)
    print("Done.")  # endregion

    # region ----- Set Vgs to 0 V -----
    print(f"Sweeping Vgs from {fet.vgs[-1]:.3f} V to 0 V... ", end="")
    for x in linspace(fet.vgs[-1], 0, int(ceil(abs(fet.vgs[-1]) / settings.smu_vgs.ramp_step) + 1)):
        smu_vgs.set_bias_level(bias=x, delay=settings.smu_vgs.ramp_delay)
    print("Done.")  # endregion

if sweep == 2:

    t0 = datetime.datetime.now().timestamp()

    # region ----- Measure and plot in real time -----
    print("Measuring... ", end="")
    for j in range(len(fet.vds)):

        # region ----- Set vds -----
        if j == 0 and fet.vds[0] != 0:
            for x in linspace(0, fet.vds[j], int(ceil(abs(fet.vds[j] - 0) / settings.smu_vds.ramp_step) + 1)):
                smu_vds.set_bias_level(bias=x, delay=settings.smu_vds.ramp_delay)
        else:
            smu_vds.set_bias_level(bias=fet.vds[j], delay=settings.smu_vds.delay)
        # endregion

        # region ----- Get data -----
        fet.data[0, j, 2], fet.data[0, j, 3] = smu_vds.read()  # return source, measure
        fet.data[0, j, 4] = floor(0 / (len(fet.vgs) / vgs[5]))  # store number of vgs iteration, starting from 0
        fet.data[0, j, 5] = floor(j / (len(fet.vds) / vds[5]))  # store number of vds iteration, starting from 0
        fet.data[0, j, 6] = datetime.datetime.now().timestamp() - t0  # store datetime
        # endregion

        # region ----- Update figure -----
        plot1.ax0.lines[0].set_data(fet.data[0, 0: j + 1, 2], fet.data[0, 0: j + 1, 3])
        plot1.ax0.relim()
        plot1.ax0.autoscale_view(scalex=False, scaley=True)
        plot1.ax1.lines[0].set_data(fet.data[0, 0: j + 1, 2], log(abs(fet.data[0, 0: j + 1, 3])))
        plot1.ax1.relim()
        plot1.ax1.autoscale_view(scalex=False, scaley=True)
        plt.pause(1e-3)
        # endregion

    print("Done.")  # endregion

    # region ----- Save data and figure to disc -----
    print("Saving data to disc...", end="")
    experiment.data = fet
    if os.path.exists(experiment.filename):
        if os.path.exists(experiment.backup_filename):
            os.remove(experiment.backup_filename)
        os.rename(experiment.filename, experiment.backup_filename)
    with open(experiment.filename, "wb") as file:
        pickle.dump(experiment, file)

    if os.path.exists(fig_name):
        if os.path.exists(fig_backup_name):
            os.remove(fig_backup_name)
        os.rename(fig_name, fig_backup_name)
    plt.savefig(fname=fig_name, format="png")

    if os.path.exists(experiment.filename[:-4] + "txt"):
        if os.path.exists(experiment.backup_filename[:-8] + "txt.bak"):
            os.remove(experiment.backup_filename[:-8] + "txt.bak")
        os.rename(experiment.filename[:-4] + "txt", experiment.backup_filename[:-8] + "txt.bak")
    txt = []
    for k in range(fet.data.shape[1]):
        for q in range(fet.data.shape[0]):
            txt.append(fet.data[q, k, :])
    savetxt(experiment.filename[:-4] + "txt", txt, delimiter=",", newline='\n',
            header="vgs,igs,vds,ids,vgs cycle,vds cycle, time", comments="# "+fet.comment+"\n", footer='', encoding=None)
    print("Done.")  # endregion

    # region ----- Set Vds to 0 V -----
    print(f"Sweeping Vds from {fet.vds[-1]:.3f} V to 0 V... ", end="")
    for x in linspace(fet.vds[-1], 0, int(ceil(abs(fet.vds[-1]) / settings.smu_vds.ramp_step) + 1)):
        smu_vds.set_bias_level(bias=x, delay=settings.smu_vds.delay)
    print("Done.")  # endregion

# region ----- Turn SMU(s) off -----
print("Switching off SMU(s)... ", end="")
if sweep == 0 or sweep == 1:
    smu_vgs.switch_off()
smu_vds.switch_off()
print("Done")
# endregion

# region ----- Remove backups -----
if os.path.exists(experiment.backup_filename):
    os.remove(experiment.backup_filename)
if os.path.exists(fig_backup_name):
    os.remove(fig_backup_name)
if os.path.exists(experiment.backup_filename[:-8] + "txt.bak"):
    os.remove(experiment.backup_filename[:-8] + "txt.bak")
print("measurement completed.")  # endregion

plt.show()
