# region ----- Import packages -----
import srs_sr830
import srs_srcs580
import adwin
import lakeshore_tc336
import oxford_mercury_itc
import pyvisa
import os
from numpy import mean, std, ctypeslib
from scipy.stats import linregress
import pickle
from Objects.measurement import *
from Utilities.signal_processing import *
import time
import datetime
# endregion

"""
#######################################################################
    Author:         Davide Beretta
    Date:           06.01.2022
    Description:    FET
    
    ADwin Analog Output - Analog Input configuration
    AO1: Vds     
    AO2:  
    AI1: Ids
    AI2: dVds
#######################################################################
"""

# region ----- Measurement options -----
experiment = Experiment()
experiment.experiment = "4wire-resistance"
experiment.main = r"E:\Samples\dabe"
experiment.date = datetime.datetime.now()
experiment.chip = "sample simulator"
experiment.device = "tester"
experiment.filename = f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment}.data"
experiment.backupname = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
vgs = [1, 1, 1, "lin", 0, 1]  # [list] Vgs (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
vds = [0, 1, 21, "lin", 1, 2]  # [list] Vds (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
fet = FET.Sweep(vgs, vds)  # ---------------------------------------------------------------------
fet.environment = 1  # [int] measurement environment {0: vacuum, 1: air, 2: N2, 3: Ar}
fet.illumination = 0  # [int] illumination {0: dark, 1: light}
fet.annealing = 0  # [int] {0: not annealed, 1: annealed}
fet.temperature = 273.15 + 25  # [float] temperature (in K)
fet.comment = ""
# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
t = 300  # [1D array of float] temperatures (in K).
i_th = linspace(0, 50e-6, 51)   # [1D array of float] "forward" thermometer current for iv (in A).
i_th = concatenate((i_th[:-1], flip(i_th)[:-1], (-i_th)[:-1], flip(-i_th)[:-1]))  # extends forward current sweep to cycle
# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------

# region ----- Settings ------
settings = EmptyClass()
# ----- tc settings -----
settings.__setattr__("tc", EmptyClass())
settings.tc.model = 1                       # [int] select tc model (0: lakeshore 336, 1: oxford mercury itc)
settings.tc.address = "ASRL8::INSTR"        # [string] address of temperature controller
settings.tc.t_switch = 50                   # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium"
settings.tc.sampling_freq = 1               # [int] temperature sampling frequency (in Hz)
settings.tc.settling_time_init = 0.1*1 * 60  # [float] cryostat thermalization time (in s).
settings.tc.settling_time = settings.tc.settling_time_init  # [float] cryostat thermalization time (in s).
# ----- adc settings -----
settings.__setattr__("adc", EmptyClass())
settings.adc.model = 0                      # [int] select adc model (0: adwin gold ii)
settings.adc.input_resolution = 18          # [int] input resolution (in bit)
settings.adc.output_resolution = 16         # [int] output resolution (in bit)
settings.adc.clock_freq = 300e6             # [int] clock frequency (in Hz)
settings.adc.line_freq = 50                 # [int] line frequency (in Hz)
settings.adc.scanrate = 100e3               # [int] frequency at which the script is executed (in Hz)
settings.adc.nplc = 1                       # [float] number of power line cycles
settings.adc.iv_settling_time = 0.01        # [float] measurement time (in s). The number of samples is: vt_time / (nplc / line_freq)
settings.adc.vt_settling_time = 1           # [float] measurement time (in s). The number of samples is: vt_time / (nplc / line_freq)
settings.adc.vt_measurement_time = 1        # [float] measurement time (in s). The number of samples is: vt_time / (nplc / line_freq)
settings.adc.sweep_step = 0.01              # [float] voltage sweep step (in V)
# ----- Vds source (DC bias) amplifier settings -----
settings.__setattr__("avv2", EmptyClass())
settings.avv2.model = 3                     # [int] select amplifier model {0: srs sr560, 1: tu delft XXX, 2: basel sp908, 3: bypass}
settings.avv2.address = None                # [string] address. Set None if not connected to PC
settings.avv2.gain = 0.1                      # [float] gain (in V/V) including voltage divider(s)
settings.avv2.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.coupling = None               # [string] coupling (ac or dc)
# ----- Ids signal amplifier settings -----
settings.__setattr__("avi2", EmptyClass())
settings.avi2.model = 0                     # [int] select amplifier model (0: Femto ddpca-300)
settings.avi2.address = None                # [string] address. Set None if not connected to PC
settings.avi2.gain = 1e4                    # [float] gain (in V/A)
settings.avi2.lpf = 400                     # [float] low pass filter cutoff frequency (in Hz)
settings.avi2.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi2.coupling = "dc"               # [string] coupling (ac or dc)
# ----- dVds (DC voltage across DUT) settings -----
settings.__setattr__("avv4", EmptyClass())
settings.avv4.model = 0                     # [int] select amplifier model (0: srs sr560, 1: tu delft XXX, 2: basel)
settings.avv4.address = None                # [string] address. Set None if not connected to PC
settings.avv4.gain = 1e3                    # [float] gain (in V/V)
settings.avv4.lpf = 100                     # [float] low pass filter cutoff frequency (in Hz)
settings.avv4.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv4.coupling = "dc"               # [string] coupling (ac or dc)
# ----------
experiment.settings = settings
# endregion

# region ----- Message to the user -----
print(f"""\n***** Measurement summary *****
chip: {experiment.chip}
device: {experiment.device}
temperatures: {t:.1f} K
Gate must be grounded before proceeding.""")
input("Press Enter to accept and proceed, press Ctrl-C to abort.")
# endregion

# region ----- Load drivers -----
print("\n***** Loading instrumentation drivers and configuring *****")
rm = pyvisa.ResourceManager()

if settings.adc.model == 0:
    boot_dir = "C:/ADwin/ADwin11.btl"  # directory of boot file
    routines_dir = "C:/Python scripts/lab-scripts/Instrumentation library/Adwin Gold II"  # directory of routines files
    adc = adwin.adwin(boot_dir, routines_dir)
    adc.adw.Load_Process(routines_dir + "/sweep_ao1_read_ai1.TB1")  # Load sweep AO1 and read AI1
    adc.adw.Load_Process(routines_dir + "/sweep_ao2_read_ai2.TB2")  # Load sweep AO2 and read AI2
    adc.adw.Load_Process(routines_dir + "/sweep_ao1-2_read_ai1-2.TB3")  # Load sweep AO2 and read AI2
    adc.adw.Load_Process(routines_dir + "/read_ai1-10.TB4")  # Load read AI1-10
    adc.adw.Load_Process(routines_dir + "/sweep_ao1.TB5")  # Load sweep AO1-2
    adc.adw.Load_Process(routines_dir + "/sweep_ao2.TB6")  # Load sweep AO1-2
    adc.adw.Load_Process(routines_dir + "/sweep_ao1-2.TB7")  # Load sweep AO1-2
    adc.adw.Set_Processdelay(1, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(2, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(3, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(4, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(5, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(6, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    adc.adw.Set_Processdelay(7, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
    # n. of points to average in hardware = nplc / line freq * scanrate
    adc.adw.Set_Par(33, int(ceil(settings.adc.nplc / settings.adc.line_freq * settings.adc.scanrate)))
    # in hardware settling time: no. of loops to wait after setting output)
    adc.adw.Set_Par(34, int(ceil(settings.adc.iv_settling_time * settings.adc.scanrate)))
    # number of samples of a time-dependent measurement = time / nplc * line_freq
    adc.adw.Set_Par(71, int(ceil((settings.adc.vt_settling_time + settings.adc.vt_measurement_time) / (settings.adc.nplc / settings.adc.line_freq))))
    # set initial values of AO1 and AO2
    adc.adw.Set_Par(51, adc.voltage2bin(0, bits=settings.adc.output_resolution))
    adc.adw.Set_Par(52, adc.voltage2bin(0, bits=settings.adc.output_resolution))
    print(f"ADC-DAC: ADwin Gold II drivers loaded and configured.")
# endregion

# region ----- Set or create current directory where to save files -----
print("\n***** Measurement log *****")
path = rf"{experiment.main}\{experiment.chip}\{experiment.device}\{experiment.experiment}\\"
try:
    os.chdir(path)  # if path exists, then make it cwd
    print(f"{path} ... found.")
except OSError:  # if path does not exists
    print(f"{path} ... not found. Making directory... ")
    os.makedirs(path)  # make new directory
    os.chdir(path)  # make path cwd
print(f"Current working directory set to: {os.getcwd()}")
# endregion

# region ----- Initialize figures -----
print("Initializing figure... ", end="")
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
plot1 = Figure.PlotLine(xlabel=r"$I_{DS}$ (A)", ylabel=r"$\Delta V$ (V)", obs=[r"$I_{DS}$"])
plt.show(block=False)
plt.pause(0.25)
print("Done.")  # endregion

# region ----- Make iv -----
print("Making iv(s)... ", end="")
adc.adw.SetData_Long(list(adc.voltage2bin(fet.vds / settings.avv2.gain, bits=settings.adc.output_resolution)), 21, 1, len(fet.vds))
adc.adw.Set_Par(41, len(fet.vds))  # set length of AO-AI arrays
adc.adw.Start_Process(3)
idx_ = 0
while True:
    if adc.adw.Process_Status(3):
        idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
    else:
        idx = adc.adw.Get_Par(35)  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
    if idx > idx_:
        ai1 = ctypeslib.as_array(adc.adw.GetData_Float(1, idx_ + 1, idx - idx_))
        fet.data[0, idx_: idx, 3] = adc.bin2voltage(ai1, bits=settings.adc.input_resolution) / settings.avi2.gain
        ai2 = ctypeslib.as_array(adc.adw.GetData_Float(2, idx_ + 1, idx - idx_))
        fet.data[0, idx_: idx, 7] = adc.bin2voltage(ai2, bits=settings.adc.input_resolution) / settings.avv4.gain
        fet.data[0, idx_: idx, 2] = fet.vds[idx_: idx] / settings.avv2.gain
        plot1.ax.lines[0].set_data(fet.data[0, 0: idx, 3], fet.data[0, 0: idx, 2])
        idx_ = idx
    plot1.ax.relim()
    plot1.ax.autoscale_view()
    plt.pause(0.1)
    if idx == len(fet.vds):
        break
print("Done.")  # endregion

# region ----- Save data to disc -----
print("Saving data to disc... ", end="")
experiment.data = fet
if os.path.exists(experiment.filename):
    if os.path.exists(experiment.backupname):
        os.remove(experiment.backupname)
    os.rename(experiment.filename, experiment.backupname)
with open(experiment.filename, "wb") as file:
    pickle.dump(experiment, file)
print("Done.")

print("Saving figure to disc... ", end="")
plot1.fig.savefig(fname=f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment}.png", format="png", dpi=300)
print("Done.")
# endregion

plt.show(block=False)
input("Measurement complete. Press Enter to terminate.")
exit()
