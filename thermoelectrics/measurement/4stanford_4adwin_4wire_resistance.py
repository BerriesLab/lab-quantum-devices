from instrumentation_library.adwin_gold_ii import ADwinGoldII
from instrumentation_library.lakeshore_tc336 import Lakeshore336
from instrumentation_library.passive_voltage_divider import PassiveVoltageDivider
from instrumentation_library.femto_ddpca300 import FemtoDDPCA300
from instrumentation_library.srs_sr560 import SR560
import pyvisa
from numpy import ctypeslib
import pickle
from classes.measurement import *
import datetime

"""
#######################################################################
    Author:         Davi1de Beretta
    Date:           06.01.2022
    Description:    Make an IV in 4-wire configuration
    
    ADwin Analog Output - Analog Input configuration
    AO1: Vds     
    AO2: ... 
    AI1: Ids
    AI2: dVds
#######################################################################
"""
rm = pyvisa.ResourceManager()

# Initialize an experiment object
experiment = Experiment(
    main_path=r"E:\Samples\dabe",
    experiment_name="4wire-resistance",
    date=datetime.datetime.now(),
    chip="sample simulator",
    device="tester",
)

# Initialize instrumentation
tc = Lakeshore336(
    address="ASRL8::INSTR",
    t_switch=50,
    sampling_freq=1,
    settling_time_init=0.1 * 1 * 60,
    settling_time=0.1 * 1 * 60
)
adc = ADwinGoldII(
    adwin_boot_dir="C:/ADwin/ADwin11.btl",
    adwin_routines_dir="C:/Python scripts/lab-scripts/instrumentation_library/adwin_gold_ii_routines",
    input_resolution=18,
    output_resolution=16,
    clock_freq=300e6,
    line_freq=50,
    scan_rate=100e3,
    n_plc=1,
    iv_settling_time=0.01,
    vt_settling_time=1,
    vt_measurement_time=1,
    sweep_step=0.01,
    process=["sweep_ao1_read_ai1.TB1",
             "sweep_ao2_read_ai2.TB2",
             "sweep_ao1-2_read_ai1-2.TB3",
             "read_ai1-8.TB4",
             "sweep_ao1.TB5",
             "sweep_ao2.TB6",
             "sweep_ao1-2.TB7"]
)
avv1 = PassiveVoltageDivider(
    gain=0.1
)
avi1 = FemtoDDPCA300(
    visa=,
    dll=None,
    address=None,
    gain=1e4,
    lpf=400,
    hpf=0.0,
    coupling="dc",
)
avv2 = SR560(
    address=None,
    gain=1e3,
    lpf=100,
    hpf=None,
    coupling="dc",
)


# Initialize experiment
fet = FET.Sweep(
    vgs=[0, 0, 1, "lin", 0, 1],  # start, stop, steps (>0), lin-log, mode {0: FWD, 1: FWD-BWD, 2: LOOP}, cycles
    vds=[0, 1, 21, "lin", 1, 2],  # start, stop, steps (>0), lin-log, mode {0: FWD, 1: FWD-BWD, 2: LOOP}, cycles,
    other={
        "temperature": 273.15 + 25,
        "illumination": 0,  # {0: dark, 1: light}
        "environment": 1,  # {0: vacuum, 1: air, 2: N2, 3: Ar}
        "annealing": 0,  # {0: not annealed, 1: annealed}
    }
)
    
print("\n***** measurement log *****")
path = f"{experiment.main_path}/{experiment.chip}/{experiment.device}/{experiment.experiment_name}"
# Set the directory as the current working directory
if not os.path.exists(path):
    print(f"{path} ... not found. Making directory... ")
    os.makedirs(path)
os.chdir(path)
print(f"Current working directory set to: {os.getcwd()}")

print("Initializing figure... ", end="")
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
plot1 = Figure.PlotLine(xlabel=r"$I_{DS}$ (A)", ylabel=r"$\Delta V$ (V)", obs=[r"$I_{DS}$"])
plt.show(block=False)
plt.pause(0.25)
print("Done.")

print("Making iv(s)... ", end="")
adc.adw.SetData_Long(list(adc.voltage2bin(fet.vds / avv1.gain, bits=adc.output_resolution)), 21, 1, len(fet.vds))
adc.adw.Set_Par(41, len(fet.vds))  # set length of AO-AI arrays
adc.adw.Start_Process(3)
idx_ = 0
while True:
    if adc.adw.Process_Status(3):
        # PAR35 is the scan index -> N. of completed readings is idx_scan - 1
        idx = adc.adw.Get_Par(35) - 1
    else:
        idx = adc.adw.Get_Par(35)
    if idx > idx_:
        ai1 = ctypeslib.as_array(adc.adw.GetData_Float(1, idx_ + 1, idx - idx_))
        fet.data[0, idx_: idx, 3] = adc.bin2voltage(ai1, bits=adc.input_resolution) / avi1.gain
        ai2 = ctypeslib.as_array(adc.adw.GetData_Float(2, idx_ + 1, idx - idx_))
        fet.data[0, idx_: idx, 7] = adc.bin2voltage(ai2, bits=adc.input_resolution) / avv2.gain
        fet.data[0, idx_: idx, 2] = fet.vds[idx_: idx] / avv1.gain
        plot1.ax.lines[0].set_data(fet.data[0, 0: idx, 3], fet.data[0, 0: idx, 2])
        idx_ = idx
    plot1.ax.relim()
    plot1.ax.autoscale_view()
    plt.pause(0.1)
    if idx == len(fet.vds):
        break
print("Done.")  # endregion

# region ----- Save data to disc -----
print("Savi1ng data to disc... ", end="")
experiment.data = fet
if os.path.exists(experiment.filename):
    if os.path.exists(experiment.backup_filename):
        os.remove(experiment.backup_filename)
    os.rename(experiment.filename, experiment.backup_filename)
with open(experiment.filename, "wb") as file:
    pickle.dump(experiment, file)
print("Done.")

print("Savi1ng figure to disc... ", end="")
plot1.fig.savefig(
    fname=f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment_name}.png",
    format="png", dpi=300)
print("Done.")
# endregion

plt.show(block=False)
input("measurement complete. Press Enter to terminate.")
exit()
