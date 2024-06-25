# region ----- Import packages -----
import adwin
import oxford_mercury_itc
import pyvisa
import os
from numpy import ctypeslib, log10, floor
import pickle
from Objects.Backup.measurement_objects import *
from Objects.Backup.plot_objects import *
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
sweep = 1  # [int] select experiment between "3 terminal vgs sweep" (0) and "3 terminal vds sweep" (1)
# measurement(s) options -----------------------------------------------------------------------------------------------
experiment = Experiment()
experiment.experiment = f"fet - {sweep}"
experiment.main = r"E:\Samples\dabe"
experiment.date = datetime.datetime.now()
experiment.chip = "teps02"
experiment.device = "d2"
experiment.filename = f"{experiment.chip} - {experiment.device} - {experiment.experiment}.data"
experiment.backupname = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
vgs = [0, 0, 1, "lin", 0, 1]            # [list] Vgs (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles
vds = [0, 1, 100, "lin", 0, 1]          # [list] Vds (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles
fet = FET.Sweep(1, vgs, vds)  # ---------------------------------------------------------------------
fet.environment = 0                     # [int] measurement environment {0: vacuum, 1: air, 2: N2, 3: Ar}
fet.illumination = 0                    # [int] illumination {0: dark, 1: light}
fet.temperature = 200                   # [float] temperature (in K)
fet.channel_length = None               # [float] channel length (in m)
fet.channel_width = None                # [float] channel length (in m)
fet.channel_thickness = None            # [float] channel thickness (in m)
fet.channel_material = "c60"            # [string] channel material (lowercase IUPAC)
fet.oxide_material = "sio2"             # [string] oxide material (lowercase IUPAC)
fet.oxide_thickness = 285e-9            # [float] oxide thickness (in m)
fet.source_material = "au"              # [string] source material (lowercase IUPAC)
fet.source_area = None                  # [float] source area (in m2)
fet.drain_material = "au"               # [string] drain material (lowercase IUPAC)
fet.drain_area = None                   # [float] drain area (in m2)
fet.comment = ""
vds_divider = 1
vgs_divider = 1
rgs = 1e9                           # [float] resistance used to measure the gate leakage current
comment = ""
# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------

# region ----- Settings ------
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
settings.adc.model = 0                      # [int] select adc model (0: adwin gold ii)
settings.adc.input_resolution = 18          # [int] input resolution (in bit)
settings.adc.output_resolution = 16         # [int] output resolution (in bit)
settings.adc.clock_freq = 300e6             # [int] clock frequency (in Hz)
settings.adc.line_freq = 50                 # [int] line frequency (in Hz)
settings.adc.scanrate = 50e3                # [int] frequency at which the script is executed (in Hz)
settings.adc.nplc = 1                      # [float] number of power line cycles
settings.adc.iv_settling_time = 0.1         # [float] settling time (in s) before recording data
settings.adc.vt_settling_time = 60 * 5      # [float] measurement settling time (in s). The number of samples is: vt_settling_time / (nplc / line_freq)
settings.adc.vt_measurement_time = 60 * 1   # [float] measurement time (in s). The number of samples is: vt_measurement_time / (nplc / line_freq)
# ----- Vgs source settings -----
settings.__setattr__("avv1", EmptyClass())
settings.avv1.model = 2                     # [int] select amplifier model (0: srs sr560, 1: tu delft XXX, 2: basel sp908)
settings.avv1.address = None                # [string] address. Set None if not connected to PC
settings.avv1.gain = 10                    # [float] gain (in V/V)
settings.avv1.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Vds source settings -----
settings.__setattr__("avv2", EmptyClass())
settings.avv2.model = 2                     # [int] select amplifier model (0: srs sr560, 1: tu delft XXX, 2: basel sp908)
settings.avv2.address = None                # [string] address. Set None if not connected to PC
settings.avv2.gain = 100e-6                    # [float] gain (in V/V)
settings.avv2.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Igs amplifier settings -----
settings.__setattr__("avv3", EmptyClass())
settings.avv3.model = 1                     # [int] select amplifier model (0: Femto ddpca-300, 1: stanford sr560)
settings.avv3.address = None                # [string] address. Set None if not connected to PC
settings.avv3.gain = 1e2                    # [float] gain (in V/A)
settings.avv3.lpf = 1000                     # [float] low pass filter cutoff frequency (in Hz)
settings.avv3.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv3.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Ids amplifier settings -----
settings.__setattr__("aiv1", EmptyClass())
settings.aiv1.model = 0                     # [int] select amplifier model (0: Femto ddpca-300)
settings.aiv1.address = None                # [string] address. Set None if not connected to PC
settings.aiv1.gain = 1e4                    # [float] gain (in V/A)
settings.aiv1.lpf = 500                     # [float] low pass filter cutoff frequency (in Hz)
settings.aiv1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.aiv1.coupling = "dc"               # [string] coupling (ac or dc)
# ----------
experiment.settings = settings
# endregion

# region ----- Message to the user -----
print(f"""\n***** Measurement summary *****
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
    routines_dir = "C:/Python scripts/lab-scripts/Instrumentation library/Adwin/Gold II"  # directory of routines files
    adc = adwin.adwin(boot_dir, routines_dir)
    adc.adw.Load_Process(routines_dir + "/sweep_2_ao_read_2_ai_xxx.TB1")
    adc.adw.Set_Processdelay(1, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Load_Process(routines_dir + "/read_8_ai_gold_ii.TB2")
    adc.adw.Set_Processdelay(2, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Load_Process(routines_dir + "/sweep_2_ao_xxx.TB4")
    adc.adw.Set_Processdelay(4, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    # n. of points to average in hardware = nplc / line freq * scanrate
    adc.adw.Set_Par(33, int(ceil(settings.adc.nplc / settings.adc.line_freq * settings.adc.scanrate)))
    # in hardware settling time: no. of loops to wait after setting output)
    adc.adw.Set_Par(34, int(ceil(settings.adc.iv_settling_time * settings.adc.scanrate)))
    # number of samples of a time-dependent measurement = time / nplc * line_freq
    adc.adw.Set_Par(71, int(ceil((settings.adc.vt_settling_time + settings.adc.vt_measurement_time) / (settings.adc.nplc / settings.adc.line_freq))))
    adc.adw.Set_Par(21, 1)  # set ao1 ON (Vgs)
    adc.adw.Set_Par(22, 1)  # set ao2 ON (Vds)
    adc.adw.Set_Par(51, adc.voltage2bin(0, bits=settings.adc.output_resolution))  # initialize AO1 to 0 V
    adc.adw.Set_Par(52, adc.voltage2bin(0, bits=settings.adc.output_resolution))  # initialize AO2 to 0 V
    print(f"ADC-DAC: ADwin Gold II drivers loaded and configured.")

if settings.tc.address is not None and settings.tc.model == 0:
    tc = lakeshore_tc336.tc336(visa=rm.open_resource(settings.tc.address))
    print(f"Temperature controller: {tc.read_model()} drivers loaded.")
if settings.tc.address is not None and settings.tc.model == 1:
    tc = oxford_mercury_itc.mercuryitc(visa=rm.open_resource(settings.tc.address))
    print(f"Temperature controller: {tc.read_model()} drivers loaded.")
# endregion

# region ----- Set or create current directory where to save files -----
print("\n***** Measurement log *****")
path = rf"{experiment.main}\{experiment.chip}\{experiment.device}\fet\{'vgs sweep' if sweep == 0 else 'vds sweep'}"
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
plot1 = PlotFET(vgs=vgs, vds=vds, sweep=sweep)
fig_name = f"{experiment.filename[:-4]}png"
fig_backup_name = fig_name + ".bak"
print("Done.")  # endregion

if sweep == 0:

    for idx_vds, val_vds in enumerate(fet.vds):

        # region ----- Make and load arrays in microcontroller -----
        val_vds_ = adc.bin2voltage(adc.adw.Get_Par(52), bits=settings.adc.output_resolution)  # read current AO2 value
        print(f"Setting DC bias from {val_vds_:.4f} V to {val_vds:.4f} V... ", end="")

        if val_vds_ != val_vds:  # if current AO1 value is different from setpoint

            vgs_steps = int((val_vds_ - val_vds) / (fet.vgs[1] - fet.vgs[0]))
            data_vds = linspace(val_vds_, val_vds, vgs_steps) / settings.avv1.gain / vgs_divider

            bins_vgs = adc.voltage2bin(zeros(len(data_vds)))  # keep the Vgs voltage at 0 V
            bins_vds = adc.voltage2bin(data_vds)

            adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set ao1 data
            adc.adw.Set_Par(41, len(bins_vgs))  # set length of ao1 array

            adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set ao2 data
            adc.adw.Set_Par(42, len(bins_vds))  # set length of ao2 array
        # endregion

        # region ----- Run process 4 -----
        adc.adw.Start_Process(4)
        while adc.process_status(4) is True:
            plt.pause(1e-3)
        print("Done.")  # endregion

        # region ----- Make and load arrays in microcontroller -----
        bins_vgs = adc.voltage2bin(fet.vgs / settings.avv1.gain / vgs_divider)
        bins_vds = adc.voltage2bin(ones(len(fet.vgs)) * val_vds / settings.avv2.gain / vds_divider)

        adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set ao1 data
        adc.adw.Set_Par(41, len(bins_vgs))  # set length of ao1 array

        adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set ao2 data
        adc.adw.Set_Par(42, len(bins_vds))  # set length of ao2 array
        # endregion

        # region ----- Run process 1 (and plot in real time) -----
        print("Measuring... ", end="")
        idx_ = 0
        adc.adw.Start_Process(1)
        while True:  # scan index must be > 1 to have at least 1 completed measurement in adc memory to query
            idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
            if idx > idx_:

                # read bins from microcontroller
                bins_ai1 = ctypeslib.as_array(adc.adw.GetData_Double(11, idx_ + 1, idx - idx_))
                bins_ai2 = ctypeslib.as_array(adc.adw.GetData_Double(12, idx_ + 1, idx - idx_))

                # convert bins to currents
                ai1 = adc.bin2voltage(bins_ai1, bits=settings.adc.input_resolution) / settings.avv3.gain / rgs
                ai2 = adc.bin2voltage(bins_ai2, bits=settings.adc.input_resolution) / settings.aiv1.gain

                # store currents in object
                fet.data[idx_: idx, idx_vds, 0] = fet.vgs[idx_: idx]  # vgs
                fet.data[idx_: idx, idx_vds, 1] = ai1  # igs
                fet.data[idx_: idx, idx_vds, 2] = val_vds * ones(idx-idx_)  # vds
                fet.data[idx_: idx, idx_vds, 3] = ai2  # ids
                fet.data[idx_: idx, idx_vds, 4] = floor(linspace([idx_, idx], idx-idx_, False) / (len(fet.vgs) / vgs[5]))
                fet.data[idx_: idx, idx_vds, 5] = floor(idx_vds / (len(fet.vds) / vds[5]))

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

            if idx == len(fet.vds):
                break

        print("Done.")  # endregion

        # region ----- Save data and figure to disc -----
        experiment.data = fet
        if os.path.exists(experiment.filename):
            if os.path.exists(experiment.backupname):
                os.remove(experiment.backupname)
            os.rename(experiment.filename, experiment.backupname)
        with open(experiment.filename, "wb") as file:
            pickle.dump(experiment, file)

        if os.path.exists(fig_name):
            if os.path.exists(fig_backup_name):
                os.remove(fig_backup_name)
            os.rename(fig_name, fig_backup_name)
        plt.savefig(fname=fig_name, format="png")  # endregion

if sweep == 1:

    for idx_vgs, val_vgs in enumerate(fet.vgs):

        # region ----- Make and load arrays in microcontroller -----
        val_vgs_ = adc.bin2voltage(adc.adw.Get_Par(51), bits=settings.adc.output_resolution)  # read current AO1 value
        print(f"Setting Vgs from {val_vgs_:.4f} V to {val_vgs:.4f} V... ", end="")

        if val_vgs_ != val_vgs:  # if current AO1 value is different from setpoint

            vgs_steps = int((val_vgs_ - val_vgs) / (fet.vds[1] - fet.vds[0]))
            data_vgs = linspace(val_vgs_, val_vgs, vgs_steps) / settings.avv1.gain / vgs_divider

            bins_vgs = adc.voltage2bin(data_vgs)
            bins_vds = adc.voltage2bin(zeros(len(data_vgs)))  # keep the Vds voltage at 0 V

            adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set ao1 data
            adc.adw.Set_Par(41, len(bins_vgs))  # set length of ao1 array

            adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set ao2 data
            adc.adw.Set_Par(42, len(bins_vds))  # set length of ao2 array
        # endregion

        # region ----- Run process 4 -----
        adc.adw.Start_Process(4)
        while adc.process_status(4) is True:
            plt.pause(1e-3)
        print("Done.")  # endregion

        # region ----- Make and load arrays in microcontroller -----
        bins_vgs = adc.voltage2bin(ones(len(fet.vds)) * val_vgs / settings.avv1.gain / vgs_divider)
        bins_vds = adc.voltage2bin(fet.vds / settings.avv2.gain / vds_divider)

        adc.adw.SetData_Long(list(bins_vgs), 21, 1, len(bins_vgs))  # set ao1 data
        adc.adw.Set_Par(41, len(bins_vgs))  # set length of ao1 array

        adc.adw.SetData_Long(list(bins_vds), 22, 1, len(bins_vds))  # set ao2 data
        adc.adw.Set_Par(42, len(bins_vds))  # set length of ao2 array
        # endregion

        # region ----- Run process 1 (and plot in real time) -----
        print("Measuring... ", end="")
        idx_ = 0
        adc.adw.Start_Process(1)
        while True:  # scan index must be > 1 to have at least 1 completed measurement in adc memory to query
            idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
            if idx > idx_:

                # read bins from microcontroller
                bins_ai1 = ctypeslib.as_array(adc.adw.GetData_Double(11, idx_ + 1, idx - idx_))
                bins_ai2 = ctypeslib.as_array(adc.adw.GetData_Double(12, idx_ + 1, idx - idx_))

                # convert bins to currents
                ai1 = adc.bin2voltage(bins_ai1, bits=settings.adc.input_resolution) / settings.avv3.gain / rgs
                ai2 = adc.bin2voltage(bins_ai2, bits=settings.adc.input_resolution) / settings.aiv1.gain

                # store currents in object
                fet.data[idx_vgs, idx_: idx, 0] = fet.vgs[idx_: idx]  # vgs
                fet.data[idx_vgs, idx_: idx, 1] = ai1  # igs
                fet.data[idx_vgs, idx_: idx, 2] = val_vds * ones(idx-idx_)  # vds
                fet.data[idx_vgs, idx_: idx, 3] = ai2  # ids
                fet.data[idx_vgs, idx_: idx, 4] = floor(linspace([idx_, idx], idx-idx_, False) / (len(fet.vds) / vds[5]))

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

            plt.pause(1e-3)

            if idx == len(vds):
                break

        print("Done.")  # endregion

        # region ----- Save data and figure to disc -----
        experiment.data = fet
        if os.path.exists(experiment.filename):
            if os.path.exists(experiment.backupname):
                os.remove(experiment.backupname)
            os.rename(experiment.filename, experiment.backupname)
        with open(experiment.filename, "wb") as file:
            pickle.dump(experiment, file)

        if os.path.exists(fig_name):
            if os.path.exists(fig_backup_name):
                os.remove(fig_backup_name)
            os.rename(fig_name, fig_backup_name)
        plt.savefig(fname=fig_name, format="png")  # endregion

plt.show()
