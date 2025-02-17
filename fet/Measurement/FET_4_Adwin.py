# region ----- Import packages -----
import time
import adwin
import pyvisa
import os
from numpy import ctypeslib, log10, floor, ones
import pickle
from Objects.measurement import *
from Utilities.signal_processing import *
import datetime
# endregion

"""
#######################################################################
    Author:         Davide Beretta
    Date:           30.12.2021
    Description:    FET
    
    Instrumentation settings are remotely set and controlled only if
    the user provides the interface address.
    This script can also be used to make IVs (simply ignore AI1).
    
    ADwin Analog Output - Analog Input configuration
    AO1: Vgs
    AO2: Vds
    AI1: Igs
    AI2: Ids
#######################################################################
"""

# region ----- USER inputs -----
sweep = 2   # [int] {0: transfer characteristic, 1: output characteristic, 2: iv}
# measurement(s) options -----------------------------------------------------------------------------------------------
experiment = Experiment()
experiment.experiment_name = str({0: "transfer characteristic", 1: "output characteristic", 2: "iv"}[sweep])
experiment.main_path = r"E:\Samples\dabe"
experiment.date = datetime.datetime.now()
experiment.architecture = "tetra_fet_01"  # {0: tetra fet, 1: osja}
experiment.chip = "tep_ch3_11"
experiment.device = "a2"
experiment.filename = f"{experiment.date.strftime('%Y.%m.%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment_name}.data"
experiment.backup_filename = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
vgs = [0, 0, 1, "lin", 0, 1]  # [list] Vgs (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
vds = [0.000, 0.001, 51, "lin", 2, 1]  # [list] Vds (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
fet = FET.Sweep(vgs, vds)  # ---------------------------------------------------------------------
fet.environment = 1  # [int] measurement environment {0: vacuum, 1: air, 2: N2, 3: Ar}
fet.illumination = 0  # [int] illumination {0: dark, 1: light}
fet.annealing = 0  # [int] {0: not annealed, 1: annealed}
fet.temperature = 273.15 + 25  # [float] temperature (in K)
fet.comment = ""
# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------

# region ----- settings ------
settings = EmptyClass()
# ----- tc settings -----
settings.__setattr__("tc", EmptyClass())
settings.tc.model = 1                       # [int] select tc model (0: lakeshore 336, 1: oxford mercury itc)
settings.tc.address = None  # "ASRL8::INSTR"        # [string] address of temperature controller
settings.tc.t_switch = 50                   # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium"
settings.tc.sampling_freq = 1               # [int] temperature sampling frequency (in Hz)
settings.tc.settling_time = 15 * 60         # [float] cryostat thermalization time (in s).
settings.tc.settling_time_init = 1 * 1 * 60    # [float] cryostat initial thermalization time (in s).
settings.tc.settling_time_after_heater_sweep = settings.tc.settling_time  # [float] cryostat thermalization time (in s) after heater sweep.
# ----- adc settings -----
settings.__setattr__("adc", EmptyClass())
settings.adc.model = 0                      # [int] select adc model (0: ADwinGoldII gold ii)
settings.adc.input_resolution = 18          # [int] input resolution (in bit)
settings.adc.output_resolution = 16         # [int] output resolution (in bit)
settings.adc.clock_freq = 300e6             # [int] clock frequency (in Hz)
settings.adc.line_freq = 50                 # [int] line frequency (in Hz)
settings.adc.scan_rate = 100e3                # [int] frequency at which the script is executed (in Hz)
settings.adc.n_plc = 1                      # [float] number of power line cycles
settings.adc.iv_settling_time = 0.1         # [float] settling time (in s) before recording data
settings.adc.iv_settling_time_init = 0      # [float] settling time (in s) before recording first data
settings.adc.vt_settling_time = 60 * 5      # [float] measurement settling time (in s). The number of samples is: vt_settling_time / (n_plc / line_freq)
settings.adc.vt_measurement_time = 60 * 1   # [float] measurement time (in s). The number of samples is: vt_measurement_time / (n_plc / line_freq)
settings.adc.sweep_rate = 0.25               # [float] voltage sweep rate (in V/s)
settings.adc.sweep_step = 0.01             # [float] voltage sweep step (in V)
# ----- Vgs source settings -----
settings.__setattr__("avv1", EmptyClass())
settings.avv1.model = 2                     # [int] select amplifier model (0: srs sr560, 1: tu delft S1h, 2: Basel SP908)
settings.avv1.address = None                # [string] address. Set None if not connected to PC
settings.avv1.gain = 1e1                    # [float] gain (in V/V) including voltage divider(s) (e.g. 1/100)
settings.avv1.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Vds source settings -----
settings.__setattr__("avv2", EmptyClass())
settings.avv2.model = 3                     # [int] select amplifier model (0: srs sr560, 1: tu delft S4c, 2: basel sp908, 3: bypass)
settings.avv2.address = None                # [string] address. Set None if not connected to PC
settings.avv2.gain = 1e-3                      # [float] gain (in V/V) including votage divider(s) (e.g. 1/100)
settings.avv2.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.coupling = None               # [string] coupling (ac or dc)
# ----- Igs (V=RI) amplifier settings -----
settings.__setattr__("avi1", EmptyClass())
settings.avi1.model = 1                     # [int] select amplifier model (0: Femto ddpca-300, 1: stanford sr560)
settings.avi1.address = None                # [string] address. Set None if not connected to PC
settings.avi1.gain = 1e3 * 100e3            # [float] gain (in V/A). When the amplifier is V/V, the gain is "Gain*Resistance"
settings.avi1.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi1.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Ids amplifier settings -----
settings.__setattr__("avi2", EmptyClass())
settings.avi2.model = 0                     # [int] select amplifier model (0: Femto ddpca-300)
settings.avi2.address = None                # [string] address. Set None if not connected to PC
settings.avi2.gain = 1e7                    # [float] gain (in V/A)
settings.avi2.lpf = 500                     # [float] low pass filter cutoff frequency (in Hz)
settings.avi2.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi2.coupling = "dc"               # [string] coupling (ac or dc)
# ----------
# ----- dV amplifier settings -----
settings.__setattr__("avv3", EmptyClass())
settings.avv3.model = 3                     # [int] select amplifier model (0: srs sr560, 1: tu delft XXX, 2: basel sp908, 3: bypass)
settings.avv3.address = None                # [string] address. Set None if not connected to PC
settings.avv3.gain = 1e4                      # [float] gain (in V/V) including votage divider(s) (e.g. 1/100)
settings.avv3.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv3.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv3.coupling = None               # [string] coupling (ac or dc)
# ----------
experiment.settings = settings
# endregion

# region ----- Message to the user -----
print(f"""\n***** measurement summary *****
chip: {experiment.chip}
device: {experiment.device}
temperatures: {fet.temperature:.1f}""")
input("Press Enter to accept and proceed, press Ctrl-C to abort.")
# endregion

# region ----- Load drivers -----
print("\n***** Loading instrumentation drivers and configuring *****")
rm = pyvisa.ResourceManager()

if settings.adc.model == 0:
    boot_dir = "C:/ADwin/ADwin11.btl"  # directory of boot file
    routines_dir = "C:/Python scripts/lab-scripts/instrumentation_library/adwin_gold_ii_routines"  # directory of routines files
    adc = adwin.ADwinGoldII(boot_dir, routines_dir)
    adc.adw.Load_Process(routines_dir + "/sweep_ao1_read_ai1.TB1")  # Load sweep AO1 and read AI1
    adc.adw.Load_Process(routines_dir + "/sweep_ao2_read_ai2.TB2")  # Load sweep AO2 and read AI2
    adc.adw.Load_Process(routines_dir + "/sweep_ao1-2_read_ai1-2.TB3")  # Load sweep AO2 and read AI2
    adc.adw.Load_Process(routines_dir + "/read_ai1-8.TB4")  # Load read AI1-8
    adc.adw.Load_Process(routines_dir + "/sweep_ao1.TB5")  # Load sweeo AO1-2
    adc.adw.Load_Process(routines_dir + "/sweep_ao2.TB6")  # Load sweeo AO1-2
    adc.adw.Load_Process(routines_dir + "/sweep_ao1-2.TB7")  # Load sweeo AO1-2
    adc.adw.Set_Processdelay(1, int(ceil(settings.adc.clock_freq / settings.adc.scan_rate)))
    adc.adw.Set_Processdelay(2, int(ceil(settings.adc.clock_freq / settings.adc.scan_rate)))
    adc.adw.Set_Processdelay(3, int(ceil(settings.adc.clock_freq / settings.adc.scan_rate)))
    adc.adw.Set_Processdelay(4, int(ceil(settings.adc.clock_freq / settings.adc.scan_rate)))
    adc.adw.Set_Processdelay(5, int(ceil(settings.adc.clock_freq / settings.adc.scan_rate)))
    adc.adw.Set_Processdelay(6, int(ceil(settings.adc.clock_freq / settings.adc.scan_rate)))
    adc.adw.Set_Processdelay(7, int(ceil(settings.adc.clock_freq / settings.adc.scan_rate)))
    # n. of points to average in hardware = n_plc / line freq * scan_rate
    adc.adw.Set_Par(33, int(ceil(settings.adc.n_plc / settings.adc.line_freq * settings.adc.scan_rate)))
    # in hardware settling time: no. of loops to wait after setting output)
    adc.adw.Set_Par(34, int(ceil(settings.adc.iv_settling_time * settings.adc.scan_rate)))
    # set initial values of AO1 and AO2
    adc.adw.Set_Par(51, adc.voltage2bin(0, bits=settings.adc.output_resolution))
    adc.adw.Set_Par(52, adc.voltage2bin(0, bits=settings.adc.output_resolution))
    print(f"ADC-DAC: ADwin Gold II drivers loaded and configured.")
# endregion

# region ----- Set or create current directory where to save files -----
print("\n***** measurement log *****")
path = rf"{experiment.main_path}\{experiment.chip}\{experiment.device}\{experiment.experiment_name}\\"
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

if sweep == 0:  # Transfer characteristic

    for idx_vds, val_vds in enumerate(fet.vds):

        # region ----- Initialize Vgs and Vds -----
        val_vgs_ = adc.bin2voltage(adc.adw.Get_Par(51), bits=settings.adc.output_resolution) * settings.avv1.gain  # read current AO1 value
        val_vds_ = adc.bin2voltage(adc.adw.Get_Par(52), bits=settings.adc.output_resolution) * settings.avv2.gain  # read current AO2 value
        print(f"Setting:\n\t"
              f"Vgs from {val_vgs_:.4f} V to {fet.vgs[0]:.4f} V\n\t"
              f"Vds from {val_vds_:.4f} V to {val_vds:.4f} V\n... ", end="")
        if val_vgs_ != vgs[0] or val_vds_ != val_vds:  # if AO1 or AO2 need to be initialized
            vgs_steps = int(ceil(abs(((val_vgs_ - fet.vgs[0]) / settings.adc.sweep_step))))
            vds_steps = int(ceil(abs(((val_vds_ - val_vds) / settings.adc.sweep_rate))))
            n_steps = max(vds_steps, vgs_steps)
            data_vgs = linspace(val_vgs_, fet.vgs[0], vgs_steps) / settings.avv1.gain  # generate voltage array
            data_vds = linspace(val_vds_, val_vds, vds_steps) / settings.avv2.gain  # generate voltage array
            bins_vgs = adc.voltage2bin(data_vgs, bits=settings.adc.output_resolution)  # generate Vgs bins array
            bins_vds = adc.voltage2bin(data_vds, bits=settings.adc.output_resolution)  # generate Vds bins array
            adc.adw.Set_Par(41, len(bins_vgs))  # set length of arrays
            adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set AO1 data
            adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set AO2 data
        adc.adw.Start_Process(7)  # Sweep AO1-2
        while adc.process_status(7) is True:
            plt.pause(0.1)
        print("Done.")  # endregion

        # region ----- Wait for steady state -----
        t0 = time.time()
        while time.time() - t0 < settings.adc.iv_settling_time_init:
            plt.pause(0.1)
        # endregion

        # region ----- Measure and plot (in real time) -----
        print("Measuring... ", end="")
        bins_vgs = adc.voltage2bin(fet.vgs / settings.avv1.gain)
        bins_vds = adc.voltage2bin(ones(len(fet.vgs)) * val_vds / settings.avv2.gain)
        adc.adw.Set_Par(41, len(bins_vgs))  # set length of arrays
        adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set AO1 data
        adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set AO2 data

        idx_ = 0
        adc.adw.Start_Process(3)  # Sweep AO1 and AO2, read AI1, AI2 and AI3
        while True:  # scan index must be > 1 to have at least 1 completed measurement in adc memory to query
            if adc.adw.Process_Status(3):
                idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
            else:
                idx = adc.adw.Get_Par(35)  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
            if idx > idx_:
                # read bins from microcontroller
                bins_ai1 = ctypeslib.as_array(adc.adw.GetData_Long(1, idx_ + 1, idx - idx_))
                bins_ai2 = ctypeslib.as_array(adc.adw.GetData_Long(2, idx_ + 1, idx - idx_))
                # convert bins to currents
                ai1 = adc.bin2voltage(bins_ai1, bits=settings.adc.input_resolution) / settings.avi1.gain
                ai2 = adc.bin2voltage(bins_ai2, bits=settings.adc.input_resolution) / settings.avi2.gain
                # store currents in object
                fet.data[idx_: idx, idx_vds, 0] = fet.vgs[idx_: idx]  # vgs
                fet.data[idx_: idx, idx_vds, 1] = ai1  # igs
                fet.data[idx_: idx, idx_vds, 2] = val_vds * ones(idx-idx_)  # vds
                fet.data[idx_: idx, idx_vds, 3] = ai2  # ids
                fet.data[idx_: idx, idx_vds, 4] = floor(linspace(idx_, idx, idx-idx_, False) / (len(fet.vgs) / vgs[5]))  # store Vgs iteration
                fet.data[idx_: idx, idx_vds, 5] = floor(idx_vds / (len(fet.vds) / vds[5]))  # store Vds iteration
                # fet.data[idx_: idx, idx_vds, 6] = datetime.datetime.now().timestamp() - t0  # store datetime
                # plot
                plot1.ax0.lines[2 * idx_vds + 0].set_data(fet.data[0: idx, idx_vds, 0], fet.data[0: idx, idx_vds, 1])
                plot1.ax0.lines[2 * idx_vds + 1].set_data(fet.data[0: idx, idx_vds, 0], fet.data[0: idx, idx_vds, 3])
                plot1.ax0.relim()
                plot1.ax0.autoscale_view(scalex=False, scaley=True)
                plot1.ax1.lines[2 * idx_vds + 0].set_data(fet.data[0: idx, idx_vds, 0], log10(abs(fet.data[0: idx, idx_vds, 1])))
                plot1.ax1.lines[2 * idx_vds + 1].set_data(fet.data[0: idx, idx_vds, 0], log10(abs(fet.data[0: idx, idx_vds, 3])))
                plot1.ax1.relim()
                plot1.ax1.autoscale_view(scalex=False, scaley=True)
                idx_ = idx
            plt.pause(1e-3)
            if idx == len(fet.vgs):
                break
        print("Done.")  # endregion

        # region ----- Save data and figure to disc -----
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
        plt.savefig(fname=fig_name, format="png", dpi=300)  # endregion

if sweep == 1:  # Output characteristic

    for idx_vgs, val_vgs in enumerate(fet.vgs):

        # region ----- Initialize Vgs and Vds -----
        val_vgs_ = adc.bin2voltage(adc.adw.Get_Par(51), bits=settings.adc.output_resolution) * settings.avv1.gain  # read current AO1 value
        val_vds_ = adc.bin2voltage(adc.adw.Get_Par(52), bits=settings.adc.output_resolution) * settings.avv2.gain  # read current AO2 value
        print(f"Setting:\n\t"
              f"Vgs from {val_vgs_:.4f} V to {val_vgs:.4f} V\n\t"
              f"Vds from {val_vds_:.4f} V to {fet.vds[0]:.4f} V\n... ", end="")
        if val_vgs_ != val_vgs or val_vds_ != fet.vds[0]:  # if AO1 or AO2 need to be initialized
            vgs_steps = int(ceil(abs(((val_vgs_ - val_vgs) / settings.adc.sweep_step))))
            vds_steps = int(ceil(abs(((val_vds_ - fet.vds[0]) / settings.adc.sweep_step))))
            n_steps = max(vds_steps, vgs_steps)
            data_vgs = linspace(val_vgs_, val_vgs, n_steps) / settings.avv1.gain
            data_vds = linspace(val_vds_, fet.vds[0], n_steps) / settings.avv2.gain
            bins_vgs = adc.voltage2bin(data_vgs, bits=settings.adc.output_resolution)
            bins_vds = adc.voltage2bin(data_vds, bits=settings.adc.output_resolution)
            adc.adw.Set_Par(41, len(bins_vgs))  # set length of arrays
            adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set AO1 data
            adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set AO2 data
        adc.adw.Start_Process(7)  # Sweep AO1-2
        while adc.process_status(7) is True:
            plt.pause(1e-3)
        print("Done.")  # endregion

        # region ----- Wait for steady state -----
        t0 = time.time()
        while time.time() - t0 < settings.adc.iv_settling_time_init:
            plt.pause(0.1)
        # endregion

        # region ----- Measure and plot (in real time) -----
        print("Measuring... ", end="")
        bins_vgs = adc.voltage2bin(ones(len(fet.vds)) * val_vgs / settings.avv1.gain, bits=settings.adc.output_resolution)
        bins_vds = adc.voltage2bin(fet.vds / settings.avv2.gain, bits=settings.adc.output_resolution)
        adc.adw.Set_Par(41, len(bins_vgs))  # set length of arrays
        adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set ao1 data
        adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set ao2 data

        idx_ = 0
        adc.adw.Start_Process(3)
        while True:  # scan index must be > 1 to have at least 1 completed measurement in adc memory to query
            if adc.adw.Process_Status(3):
                idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
            else:
                idx = adc.adw.Get_Par(35)  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
            if idx > idx_:
                # read bins from microcontroller
                bins_ai1 = ctypeslib.as_array(adc.adw.GetData_Long(1, idx_ + 1, idx - idx_))
                bins_ai2 = ctypeslib.as_array(adc.adw.GetData_Long(2, idx_ + 1, idx - idx_))
                # convert bins to currents
                ai1 = adc.bin2voltage(bins_ai1, bits=settings.adc.input_resolution) / settings.avi1.gain
                ai2 = adc.bin2voltage(bins_ai2, bits=settings.adc.input_resolution) / settings.avi2.gain
                # store currents in object
                fet.data[idx_vgs, idx_: idx, 0] = val_vgs * ones(idx-idx_)  # vgs
                fet.data[idx_vgs, idx_: idx, 1] = ai1  # igs
                fet.data[idx_vgs, idx_: idx, 2] = fet.vds[idx_: idx]  # vds
                fet.data[idx_vgs, idx_: idx, 3] = ai2  # ids
                fet.data[idx_vgs, idx_: idx, 4] = floor(idx_vgs / (len(fet.vgs) / vgs[5]))  # store Vgs iteration
                fet.data[idx_vgs, idx_: idx, 5] = floor(linspace(idx_, idx, idx-idx_, False) / (len(fet.vds) / vds[5]))  # store Vds iteration
                # fet.data[idx_: idx, idx_vds, 6] = datetime.datetime.now().timestamp() - t0  # store datetime
                # plot
                plot1.ax0.lines[2 * idx_vgs + 0].set_data(fet.data[idx_vgs, 0: idx, 2], fet.data[idx_vgs, 0: idx, 1])
                plot1.ax0.lines[2 * idx_vgs + 1].set_data(fet.data[idx_vgs, 0: idx, 2], fet.data[idx_vgs, 0: idx, 3])
                plot1.ax0.relim()
                plot1.ax0.autoscale_view(scalex=False, scaley=True)
                plot1.ax1.lines[2 * idx_vgs + 0].set_data(fet.data[idx_vgs, 0: idx, 2], log10(abs(fet.data[idx_vgs, 0: idx, 1])))
                plot1.ax1.lines[2 * idx_vgs + 1].set_data(fet.data[idx_vgs, 0: idx, 2], log10(abs(fet.data[idx_vgs, 0: idx, 3])))
                plot1.ax1.relim()
                plot1.ax1.autoscale_view(scalex=False, scaley=True)
                idx_ = idx
            plt.pause(0.1)
            if idx == len(fet.vds):
                break
        print("Done.")  # endregion

        # region ----- Save data and figure to disc -----
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
        plt.savefig(fname=fig_name, format="png", dpi=300)  # endregion

if sweep == 2:  # IV

    # region ----- Initialize Vds -----
    val_vds_ = adc.bin2voltage(adc.adw.Get_Par(52), bits=settings.adc.output_resolution) * settings.avv2.gain  # read current AO2 value
    print(f"Setting:\n\t"
          f"Vds from {val_vds_:.4f} V to {fet.vds[0]:.4f} V\n... ", end="")
    if val_vds_ != fet.vds[0]:  # if AO1 or AO2 need to be initialized
        vds_steps = int(ceil(abs(val_vds_ - fet.vds[0]) / settings.adc.sweep_step))
        data_vds = linspace(val_vds_, fet.vds[0], vds_steps) / settings.avv2.gain
        bins_vds = adc.voltage2bin(data_vds, bits=settings.adc.output_resolution)
        adc.adw.Set_Par(41, len(bins_vds))  # set length of arrays
        adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set AO2 data
    adc.adw.Start_Process(6)  # Sweep AO2
    while adc.process_status(6) is True:
        plt.pause(1e-3)
    print("Done.")  # endregion

    # region ----- Wait for steady state -----
    t0 = time.time()
    while time.time() - t0 < settings.adc.iv_settling_time_init:
        plt.pause(0.1)
    # endregion

    # region ----- Measure and plot (in real time) -----
    print("Measuring... ", end="")
    bins_vds = adc.voltage2bin(fet.vds / settings.avv2.gain, bits=settings.adc.output_resolution)
    adc.adw.Set_Par(41, len(bins_vds))  # set length of arrays
    adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set ao2 data

    idx_ = 0
    adc.adw.Start_Process(2)
    while True:  # scan index must be > 1 to have at least 1 completed measurement in adc memory to query
        if adc.adw.Process_Status(2):
            idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
        else:
            idx = adc.adw.Get_Par(35)  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
        if idx > idx_:
            # read bins from microcontroller
            bins_ai2 = ctypeslib.as_array(adc.adw.GetData_Long(2, idx_ + 1, idx - idx_))
            # convert bins to currents
            ai2 = adc.bin2voltage(bins_ai2, bits=settings.adc.input_resolution) / settings.avi2.gain
            # store currents in object
            fet.data[0, idx_: idx, 2] = fet.vds[idx_: idx]  # vds
            fet.data[0, idx_: idx, 3] = ai2  # ids
            fet.data[0, idx_: idx, 5] = floor(linspace(idx_, idx, idx-idx_, False) / (len(fet.vds) / vds[5]))  # store Vds iteration
            # plot
            plot1.ax0.lines[0].set_data(fet.data[0, 0: idx, 2], fet.data[0, 0: idx, 3])
            plot1.ax0.relim()
            plot1.ax0.autoscale_view(scalex=False, scaley=True)
            plot1.ax1.lines[0].set_data(fet.data[0, 0: idx, 2], log10(abs(fet.data[0, 0: idx, 3])))
            plot1.ax1.relim()
            plot1.ax1.autoscale_view(scalex=False, scaley=True)
            idx_ = idx
        plt.pause(0.1)
        if idx == len(fet.vds):
            break
    print("Done.")  # endregion

    # region ----- Save data and figure to disc -----
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
    plt.savefig(fname=fig_name, format="png", dpi=300)  # endregion

# region ----- Set Vds and Vgs to 0 V -----
val_vgs_ = adc.bin2voltage(adc.adw.Get_Par(51), bits=settings.adc.output_resolution) * settings.avv1.gain  # read current AO1 value
val_vds_ = adc.bin2voltage(adc.adw.Get_Par(52), bits=settings.adc.output_resolution) * settings.avv2.gain  # read current AO2 value
if val_vds_ != 0 or val_vgs_ != 0:  # if current AO1 value is different from setpoint
    print(f"Setting:\n\t"
          f"Vgs from {val_vgs_:.4f} V to {0:.4f} V\n\t"
          f"Vds from {val_vds_:.4f} V to {0:.4f} V\n... ", end="")
    vgs_steps = int(ceil(abs(((val_vgs_ - 0) / settings.adc.sweep_step))))
    vds_steps = int(ceil(abs(((val_vds_ - 0) / settings.adc.sweep_step))))
    n_steps = max(vds_steps, vgs_steps)
    data_vgs = linspace(val_vgs_, 0, n_steps) / settings.avv1.gain  # generate voltage array
    data_vds = linspace(val_vds_, 0, n_steps) / settings.avv2.gain  # generate voltage array
    bins_vgs = adc.voltage2bin(data_vgs, bits=settings.adc.output_resolution)  # generate Vgs bins array
    bins_vds = adc.voltage2bin(data_vds, bits=settings.adc.output_resolution)  # generate Vds bins array
    adc.adw.Set_Par(41, len(bins_vgs))  # set length of arrays
    adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set AO1 data
    adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set AO2 data
    if sweep == 0 or sweep == 1:
        adc.adw.Start_Process(7)  # Sweep AO1-2
        while adc.process_status(7) is True:
            plt.pause(0.1)
    elif sweep == 2:
        adc.adw.Start_Process(6)  # Sweep AO2
        while adc.process_status(6) is True:
            plt.pause(0.1)
    print("Done.")
# endregion

plt.show(block=False)
input("measurement complete. Press Enter to terminate.")
exit()
