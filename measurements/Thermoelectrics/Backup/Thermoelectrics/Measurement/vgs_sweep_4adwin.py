# region ----- Import packages -----
import srs_srcs580
import adwin
import lakeshore_tc336
import oxford_mercury_itc
import pyvisa
import os
from numpy import ctypeslib
from Objects.Backup.measurement_objects import *
from Objects.Backup.plot_objects import *
from Utilities.signal_processing import *
import datetime
# endregion

#######################################################################
#   Author:         Davide Beretta
#   Date:           03.12.2021
#   Description:    FET: Vgs sweep
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
experiment.filename = f"{experiment.chip} - {experiment.device} - {experiment.experiment}.data"
experiment.backupname = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
t = linspace(99, 109, 51)             # [1D array of float] temperatures (in K).
vgs = linspace(0, 100, 51)
vgs = concatenate((vgs[:-1], flip(vgs)[:-1], (-vgs)[:-1], flip(-vgs)[:]))  # extends forward current sweep to cycle
vds = linspace(100e-6, 100e-6, 1)
vgs_steps = 1000
vds_steps = 1000
vds_divider = 1/10
vgs_divider = 1
n = 1                             # number of cycles

# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------

# region ----- Settings ------
settings = EmptyClass()
# ----- tc settings -----
settings.__setattr__("tc", EmptyClass())
settings.tc.model = 1                       # [int] select tc model (0: lakeshore 336, 1: oxford mercury itc)
settings.tc.address = "ASRL8::INSTR"        # [string] address of temperature controller
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
settings.adc.nplc = 10                      # [float] number of power line cycles
settings.adc.iv_settling_time = 0.1         # [float] settling time (in s) before recording data
settings.adc.vt_settling_time = 60 * 5      # [float] measurement settling time (in s). The number of samples is: vt_settling_time / (nplc / line_freq)
settings.adc.vt_measurement_time = 60 * 1   # [float] measurement time (in s). The number of samples is: vt_measurement_time / (nplc / line_freq)
# ----- Vgs source settings -----
settings.__setattr__("vgs_source", EmptyClass())
settings.vgs_source.model = 2                     # [int] select amplifier model (0: srs sr560, 1: tu delft XXX, 2: basel)
settings.vgs_source.address = None                # [string] address. Set None if not connected to PC
settings.vgs_source.gain = 10                    # [float] gain (in V/V)
settings.vgs_source.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.vgs_source.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.vgs_source.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Igs amplifier settings -----
settings.__setattr__("igs_amp", EmptyClass())
settings.igs_amp.model = 0                     # [int] select amplifier model (0: Femto ddpca-300)
settings.igs_amp.address = None                # [string] address. Set None if not connected to PC
settings.igs_amp.gain = 1e6                    # [float] gain (in V/A)
settings.igs_amp.lpf = 400                     # [float] low pass filter cutoff frequency (in Hz)
settings.igs_amp.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.igs_amp.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Ids amplifier settings -----
settings.__setattr__("ids_amp", EmptyClass())
settings.ids_amp.model = 0                     # [int] select amplifier model (0: Femto ddpca-300)
settings.ids_amp.address = None                # [string] address. Set None if not connected to PC
settings.ids_amp.gain = 1e6                    # [float] gain (in V/A)
settings.ids_amp.lpf = 400                     # [float] low pass filter cutoff frequency (in Hz)
settings.ids_amp.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.ids_amp.coupling = "dc"               # [string] coupling (ac or dc)
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
    adc.adw.Load_Process(routines_dir + "/sweep_2_ao_read_2_ai.TB1")
    adc.adw.Set_Processdelay(1, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Load_Process(routines_dir + "/read_8_ai_gold_ii.TB2")
    adc.adw.Set_Processdelay(2, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Load_Process(routines_dir + "/sweep_2_ao.TB4")
    adc.adw.Set_Processdelay(4, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    # n. of points to average in hardware = nplc / line freq * scanrate
    adc.adw.Set_Par(33, int(ceil(settings.adc.nplc / settings.adc.line_freq * settings.adc.scanrate)))
    # in hardware settling time: no. of loops to wait after setting output)
    adc.adw.Set_Par(34, int(ceil(settings.adc.iv_settling_time * settings.adc.scanrate)))
    # number of samples of a time-dependent measurement = time / nplc * line_freq
    adc.adw.Set_Par(71, int(ceil((settings.adc.vt_settling_time + settings.adc.vt_measurement_time) / (settings.adc.nplc / settings.adc.line_freq))))
    print(f"ADC-DAC: ADwin Gold II drivers loaded and configured.")

if settings.tc.address is not None and settings.tc.model == 0:
    tc = lakeshore_tc336.tc336(visa=rm.open_resource(settings.tc.address))
    print(f"Temperature controller: {tc.read_model()} drivers loaded.")
if settings.tc.address is not None and settings.tc.model == 1:
    tc = oxford_mercury_itc.mercuryitc(visa=rm.open_resource(settings.tc.address))
    print(f"Temperature controller: {tc.read_model()} drivers loaded.")

if settings.src1.address is not None and settings.src1.model == 0:
    src1 = srs_srcs580.srcs580(visa=rm.open_resource(settings.src1.address))
    src1.configure(settings.src1.gain, settings.src1.response, settings.src1.shield,
                   settings.src1.isolation, "on", "on", settings.src1.compliance)
    print(f"Current source 1: {src1.read_model()} drivers loaded and configured.")

if settings.src2.address is not None and settings.src2.model == 0:
    src2 = srs_srcs580.srcs580(visa=rm.open_resource(settings.src2.address))
    src2.configure(settings.src1.gain, settings.src1.response, settings.src1.shield,
                   settings.src1.isolation, "on", "on", settings.src1.compliance)
    print(f"Current source 2: {src2.read_model()} drivers loaded and configured.")
# endregion

# region ----- Set or create current directory where to save files -----
print("\n***** Measurement log *****")
path = f"{experiment.main}\\{experiment.chip}\\{experiment.device}\\{experiment.experiment}\\{experiment.date.strftime('%Y-%m-%d %H.%M.%S')}\\"
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
data = FET.VgsSweep(t, n, vgs, vds)
print("Done.")
# endregion

# region ----- Initialize figure -----
print("Initializing figure... ", end="")
plot1 = PlotFET(t, n, x="vds")
print("Done.")  # endregion


kt = 0

for idx_t, val_t in enumerate(data.t):

    kn = 0

    for idx_vds, val_vds in enumerate(data.vds):

        # region ----- Sweep DC bias voltage -----
        val_vds_ = 0 if idx_vds == 0 else data.vds[idx_vds - 1]
        print(f"Setting DC bias from {val_vds_:.4f} V to {val_vds:.4f} V... ", end="")
        adc.adw.Set_Par(21, 0)  # set ao1 OFF
        adc.adw.Set_Par(22, 1)  # set ao2 ON

        if val_vds_ == val_vds:
            temp_vds = array([val_vds]) / vds_divider
        else:
            temp_vds = linspace(0 if idx_vds == 0 else data.vds[idx_vds - 1], data.vds[idx_vds], vds_steps) / vds_divider

        adc.adw.SetData_Long(list(adc.voltage2bin(temp_vds)), 22, 1, len(temp_vds))  # set ao2 data
        adc.adw.Set_Par(42, len(temp_vds))  # set length of ao2 array
        adc.adw.Start_Process(4)

        while adc.process_status(1) is True:
            plt.pause(1e-3)
            print(f"AO1: {adc.adw.Get_Par(51)}")
            print(f"AO2: {adc.adw.Get_Par(52)}")
        print("Done.")  # endregion

        # adc.adw.SetData_Long(list(adc.voltage2bin(data.vgs)), 21, 1, len(data.vgs))  # set ao1 data
        # adc.adw.Set_Par(41, len(data.vgs))  # set length of ao1 array
        adc.adw.SetData_Long(list(adc.voltage2bin(val_vds * ones(len(data.vgs)))), 22, 1, len(data.vgs))  # set ao2 data
        adc.adw.Set_Par(42, len(data.vgs))  # set length of ao2 array

        # region ----- Measure and real-time plot -----
        print("Measuring... ", end="")
        idx_ = 0
        adc.adw.Start_Process(1)
        while True:  # scan index must be > 1 to have at least 1 completed measurement in adc memory to query
            idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
            if idx > idx_:

                ai1 = ctypeslib.as_array(adc.adw.GetData_Double(11, idx_ + 1, idx - idx_))
                ai2 = ctypeslib.as_array(adc.adw.GetData_Double(12, idx_ + 1, idx - idx_))
                data.igs[idx_: idx] = adc.bin2voltage(ai1, bits=settings.adc.input_resolution) / settings.igs.gain
                data.ids[idx_: idx] = adc.bin2voltage(ai2, bits=settings.adc.input_resolution) / settings.ids.gain

                plot1.ax0.lines[(4 * kt * kn) + (4 * kn + 0)].set_data(data.vds[0: idx], data.igs[0:idx])
                plot1.ax0.lines[(4 * kt * kn) + (4 * kn + 1)].set_data(data.vds[0: idx], data.ids[0:idx])
                plot1.ax0.relim()
                plot1.ax0.autoscale_view(scalex=True, scaley=True)

                plot1.ax1.lines[(4 * kt * kn) + (4 * kn + 2)].set_data(data.vds[0: idx], data.igs[0:idx])
                plot1.ax1.lines[(4 * kt * kn) + (4 * kn + 3)].set_data(data.vds[0: idx], data.ids[0:idx])
                plot1.ax1.relim()
                plot1.ax1.autoscale_view(scalex=True, scaley=True)

                idx_ = idx

                print(f"AO2: {adc.adw.Get_Par(52)}")

            plt.pause(1e-3)

            if idx == len(vds):
                break

        print("Done.")  # endregion

        kn = kn + 4

    kt = kt + 1
