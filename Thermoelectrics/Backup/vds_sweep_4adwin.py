# region ----- Import packages -----
import adwin
import lakeshore_tc336
import oxford_mercury_itc
import pyvisa
import os
from numpy import ctypeslib, log10
from Objects.Backup.measurement_objects import *
from Objects.Backup.plot_objects import *
from Utilities.signal_processing import *
import datetime
# endregion

#######################################################################
#   Author:         Davide Beretta
#   Date:           03.12.2021
#   Description:    FET: Vds sweep
#
#   Instrumentation settings are remotely set and controlled only if
#   the user provides the interface address.
#
#   ADwin Analog Output - Analog Input configuration
#   AO1: Vgs
#   AO2: Vds
#   AI1: Igs
#   AI2: Ids
#######################################################################

# region ----- Measurement options -----
experiment = Experiment()
experiment.experiment = "vgs sweep"
experiment.main = r"E:\Samples\dabe"
experiment.date = datetime.datetime.now()
experiment.chip = "teps02"
experiment.device = "d2"
experiment.filename = f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment}.data"
experiment.backupname = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
t = linspace(50, 50, 1)             # [1D array of float] temperatures (in K).
vgs = linspace(0, 50, 2)  # [1D array] array of Vgs (in V)
vds = linspace(0e-6, 1, 21)  # [1D array] array of Vds (in V)
vds = concatenate((vds[:-1], flip(vds)[:-1], (-vds)[:-1], flip(-vds)[:]))  # extends forward current sweep to cycle
vgs_steps = 100
vds_steps = 100
vds_divider = 1
vgs_divider = 1
rgs = 1e9
n = 1                             # number of cycles
# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------

# region ----- Settings ------
settings = EmptyClass()
# ----- tc settings -----
settings.__setattr__("tc", EmptyClass())
settings.tc.model = 1                       # [int] select tc model (0: lakeshore 336, 1: oxford mercury itc)
settings.tc.address = None#"ASRL8::INSTR"        # [string] address of temperature controller
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
temperatures: {"".join([f"{x:.1f} K, " for x in t])}""")
input("Press Enter to accept and proceed, press Ctrl-C to abort.")
# endregion

# region ----- Load drivers -----
print("\n***** Loading instrumentation drivers and configuring *****")
rm = pyvisa.ResourceManager()

if settings.adc.model == 0:
    boot_dir = "C:/ADwin/ADwin11.btl"  # directory of boot file
    routines_dir = "C:/Python scripts/lab-scripts/Instrumentation library/Adwin/Gold II"  # directory of routines files
    adc = adwin.adwin(boot_dir, routines_dir)
    adc.adw.Load_Process(routines_dir + "/sweep_ao1_read_ai1.TB1")  # Load sweep AO1 and read AI1
    adc.adw.Load_Process(routines_dir + "/sweep_ao2_read_ai2.TB2")  # Load sweep AO2 and read AI2
    adc.adw.Load_Process(routines_dir + "/sweep_ao1-2_read_ai1-2.TB3")  # Load sweep AO2 and read AI2
    adc.adw.Load_Process(routines_dir + "/read_ai1-8.TB4")  # Load read AI1-8
    adc.adw.Load_Process(routines_dir + "/sweep_ao1.TB5")  # Load sweeo AO1-2
    adc.adw.Load_Process(routines_dir + "/sweep_ao2.TB6")  # Load sweeo AO1-2
    adc.adw.Load_Process(routines_dir + "/sweep_ao1-2.TB7")  # Load sweeo AO1-2
    adc.adw.Set_Processdelay(1, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(2, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(3, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(4, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(5, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(6, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(7, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Par(33, int(ceil(settings.adc.nplc / settings.adc.line_freq * settings.adc.scanrate)))  # n. of points to average in hardware = nplc / line freq * scanrate
    adc.adw.Set_Par(34, int(ceil(settings.adc.iv_settling_time * settings.adc.scanrate)))  # in hardware settling time: no. of loops to wait after setting output)
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
path = f"{experiment.main}\\{experiment.chip}\\{experiment.device}\\{experiment.experiment}\\"
try:
    os.chdir(path)  # if path exists, then make it cwd
    print(f"{path} ... found.")
except OSError:  # if path does not exists
    print(f"{path} ... not found. Making directory... ")
    os.makedirs(path)  # make new directory
    os.chdir(path)  # make path cwd
print(f"Current working directory set to: {os.getcwd()}")
# endregion

# region ----- Allocate RAM -----
print("Allocating RAM... ", end="")
fet = FET(t, n, vgs, vds, experiment=["vds"])
print("Done.")
# endregion

# region ----- Initialize figure -----
print("Initializing figure... ", end="")
plot1 = PlotFET(t=t, n=len(vgs), x="vds")
plot1.ax0.set_xlim([min(vds), max(vds)])
plot1.ax1.set_xlim([min(vds), max(vds)])
print("Done.")  # endregion

kt = 0

for idx_t, val_t in enumerate(t):

    kn = 0

    for idx_vgs, val_vgs in enumerate(vgs):

        # region ----- Set Vgs -----
        val_vg_ = 0 if idx_vgs == 0 else vgs[idx_vgs - 1]
        print(f"Setting DC bias from {val_vg_:.4f} V to {val_vgs:.4f} V... ", end="")

        if val_vg_ == val_vgs:
            temp_vgs = array([val_vgs]) / settings.avv1.gain / vgs_divider
        else:
            temp_vgs = linspace(0 if idx_vgs == 0 else vgs[idx_vgs - 1], vgs[idx_vgs], vgs_steps) / settings.avv1.gain / vgs_divider

        print(temp_vgs)

        # set ao1 ON (Vgs)
        adc.adw.Set_Par(21, 1)
        adc.adw.SetData_Long(list(adc.voltage2bin(temp_vgs / settings.avv1.gain / vgs_divider)), 21, 1, len(temp_vgs))  # set ao2 data
        adc.adw.Set_Par(41, len(temp_vgs))  # set length of ao2 array

        # set ao2 ON (Vds)
        adc.adw.Set_Par(22, 1)  # set ao2 ON (Vds)
        adc.adw.SetData_Long(list(adc.voltage2bin(zeros(len(temp_vgs)))), 22, 1, len(temp_vgs))  # set ao2 data
        adc.adw.Set_Par(42, len(temp_vgs))  # set length of ao2 array

        adc.adw.Start_Process(4)

        while adc.process_status(4) is True:
            plt.pause(1e-3)
        print("Done.")  # endregion

        # region ----- Measure and real-time plot -----
        adc.adw.Set_Par(21, 1)  # set ao1 ON
        adc.adw.SetData_Long(list(adc.voltage2bin(ones(len(vds)) * temp_vgs[-1] / settings.avv1.gain / vgs_divider)), 21, 1, len(vds))  # set ao1 data
        adc.adw.Set_Par(41, len(vds))  # set length of ao1 array

        adc.adw.Set_Par(22, 1)  # set ao2 ON
        adc.adw.SetData_Long(list(adc.voltage2bin(vds / settings.avv2.gain / vds_divider)), 22, 1, len(vds))  # set ao2 data
        adc.adw.Set_Par(42, len(vds))  # set length of ao2 array

        print("Measuring... ", end="")
        idx_ = 0
        adc.adw.Start_Process(1)
        while True:  # scan index must be > 1 to have at least 1 completed measurement in adc memory to query
            idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
            if idx > idx_:

                ai1 = ctypeslib.as_array(adc.adw.GetData_Double(11, idx_ + 1, idx - idx_))
                ai2 = ctypeslib.as_array(adc.adw.GetData_Double(12, idx_ + 1, idx - idx_))

                fet.data[idx_t]["vds_sweep"].data[idx_vgs]["igs"][idx_: idx] = adc.bin2voltage(ai1, bits=settings.adc.input_resolution) / settings.avv3.gain / rgs
                fet.data[idx_t]["vds_sweep"].data[idx_vgs]["ids"][idx_: idx] = adc.bin2voltage(ai2, bits=settings.adc.input_resolution) / settings.aiv1.gain

                plot1.ax0.lines[(2 * kt * kn) + (2 * kn + 0)].set_data(fet.data[idx_t]["vds_sweep"].data[idx_vgs]["vds"][0: idx], fet.data[idx_t]["vds_sweep"].data[idx_vgs]["igs"][0:idx])
                plot1.ax0.lines[(2 * kt * kn) + (2 * kn + 1)].set_data(fet.data[idx_t]["vds_sweep"].data[idx_vgs]["vds"][0: idx], fet.data[idx_t]["vds_sweep"].data[idx_vgs]["ids"][0:idx])
                plot1.ax0.relim()
                plot1.ax0.autoscale_view(scalex=False, scaley=True)

                plot1.ax1.lines[(2 * kt * kn) + (2 * kn + 0)].set_data(fet.data[idx_t]["vds_sweep"].data[idx_vgs]["vds"][0: idx], log10(abs(fet.data[idx_t]["vds_sweep"].data[idx_vgs]["igs"][0:idx])))
                plot1.ax1.lines[(2 * kt * kn) + (2 * kn + 1)].set_data(fet.data[idx_t]["vds_sweep"].data[idx_vgs]["vds"][0: idx], log10(abs(fet.data[idx_t]["vds_sweep"].data[idx_vgs]["ids"][0:idx])))
                plot1.ax1.relim()
                plot1.ax1.autoscale_view(scalex=False, scaley=True)

                idx_ = idx

            plt.pause(1e-2)

            if idx == len(vds):
                break

        print("Done.")  # endregion

        kn = kn + 2

    kt = kt + 1

plt.show()