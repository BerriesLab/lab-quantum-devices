# region ----- Import packages -----
import time
import adwin
import oxford_mercury_itc
import lakeshore_tc336
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
sweep = 2  # [int] select between "transfer characteristic" (0), "output characteristic" (1), "iv" (2)
sweepd = {0: "transfer characteristic vs temperature", 1: "output characteristic vs temperature", 2: "iv vs temperature"}
# measurement(s) options -----------------------------------------------------------------------------------------------
experiment = Experiment()
experiment.experiment = f"{sweepd[sweep]}"
experiment.main = r"C:\samples\dabe"
experiment.date = datetime.datetime.now()
experiment.architecture = "tetra_fet_00"  # {0: tetra fet, 1: osja}
experiment.chip = "au p3ht slow"
experiment.device = "4wire f-10um"
experiment.filename = f"{experiment.date.strftime('%Y.%m.%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment}.data"
experiment.backupname = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
annealing = [350, 12]               # [list] Annealing coditions. Ih the order: temperature (in K), duration (in h)
t = [350, 50, 61, "lin", 0, 1]    # [list] Vgs (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
vgs = [0, 0, 1, "lin", 0, 1]        # [list] Vgs (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
vds = [0, 5, 101, "lin", 2, 1]      # [list] Vds (in V). In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles (>0)
fet = FET.SweepVsT(make_array_4_sweep(t), make_array_4_sweep(vgs), make_array_4_sweep(vds))  # ---------------------------------------------------------------------
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
# ----- adc settings -----
settings.__setattr__("adc", EmptyClass())
settings.adc.model = 0                      # [int] select adc model (0: adwin gold ii)
settings.adc.input_resolution = 18          # [int] input resolution (in bit)
settings.adc.output_resolution = 16         # [int] output resolution (in bit)
settings.adc.clock_freq = 300e6             # [int] clock frequency (in Hz)
settings.adc.line_freq = 50                 # [int] line frequency (in Hz)
settings.adc.scanrate = 100e3                # [int] frequency at which the script is executed (in Hz)
settings.adc.nplc = 1                      # [float] number of power line cycles
settings.adc.iv_settling_time = 0.1         # [float] settling time (in s) before recording data
settings.adc.iv_settling_time_init = 0      # [float] settling time (in s) before recording first data
settings.adc.vt_settling_time = 60 * 5      # [float] measurement settling time (in s). The number of samples is: vt_settling_time / (nplc / line_freq)
settings.adc.vt_measurement_time = 60 * 1   # [float] measurement time (in s). The number of samples is: vt_measurement_time / (nplc / line_freq)
settings.adc.sweep_rate = 0.25               # [float] voltage sweep rate (in V/s)
settings.adc.sweep_step = 0.01             # [float] voltage sweep step (in V)
# ----- Vgs source settings -----
settings.__setattr__("avv1", EmptyClass())
settings.avv1.model = None                  # [int] select amplifier model (0: srs sr560, 1: tu delft S1h, 2: Basel SP908)
settings.avv1.address = None                # [string] address. Set None if not connected to PC
settings.avv1.gain = 1e1                    # [float] gain (in V/V) including voltage divider(s) (e.g. 1/100)
settings.avv1.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Vds source settings -----
settings.__setattr__("avv2", EmptyClass())
settings.avv2.model = 3                     # [int] select amplifier model (0: srs sr560, 1: tu delft S4c, 2: basel sp908, 3: bypass)
settings.avv2.address = None                # [string] address. Set None if not connected to PC
settings.avv2.gain = 1                      # [float] gain (in V/V) including votage divider(s) (e.g. 1/100)
settings.avv2.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.coupling = None               # [string] coupling (ac or dc)
# ----- Igs (V=RI) amplifier settings -----
settings.__setattr__("avi1", EmptyClass())
settings.avi1.model = None                     # [int] select amplifier model (0: Femto ddpca-300, 1: stanford sr560)
settings.avi1.address = None                # [string] address. Set None if not connected to PC
settings.avi1.gain = 1e3 * 100e3            # [float] gain (in V/A). When the amplifier is V/V, the gain is "Gain*Resistance"
settings.avi1.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi1.coupling = "dc"               # [string] coupling (ac or dc)
# ----- Ids amplifier settings -----
settings.__setattr__("avi2", EmptyClass())
settings.avi2.model = 0                     # [int] select amplifier model (0: Femto DDPCA-300, 1: Femto DLPCA-200)
settings.avi2.address = None                # [string] address. Set None if not connected to PC
settings.avi2.gain = 1e4                    # [float] gain (in V/A)
settings.avi2.lpf = 500                     # [float] low pass filter cutoff frequency (in Hz)
settings.avi2.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi2.coupling = "dc"               # [string] coupling (ac or dc)
# ----------
experiment.settings = settings
# endregion

# region ----- Message to the user -----
print(f"""\n***** Measurement summary *****
chip: {experiment.chip}
device: {experiment.device}
annealing: at {annealing[0]:.1f} K for {annealing[1]:.1f} h
temperatures: from {t[0]:.1f} K to {t[1]:.1f} K in {t[2]:.0f} steps.""")
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
    # n. of points to average in hardware = nplc / line freq * scanrate
    adc.adw.Set_Par(33, int(ceil(settings.adc.nplc / settings.adc.line_freq * settings.adc.scanrate)))
    # in hardware settling time: no. of loops to wait after setting output)
    adc.adw.Set_Par(34, int(ceil(settings.adc.iv_settling_time * settings.adc.scanrate)))
    # set initial values of AO1 and AO2
    adc.adw.Set_Par(51, adc.voltage2bin(0, bits=settings.adc.output_resolution))
    adc.adw.Set_Par(52, adc.voltage2bin(0, bits=settings.adc.output_resolution))
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

# region ----- Initialize figure -----
print("Initializing figure... ", end="")
plot0 = PlotObsT([r"$T_{stage}$", r"$T_{shield}$"], settings.tc.settling_time)
if sweep == 0:
    exit("Not yet implemented.")
    # plot1 = FET.PlotTransferCharacteristic(fet.vgs, fet.vds)
elif sweep == 1:
    exit("Not yet implemented.")
    # plot1 = FET.PlotOutputCharacteristic(fet.vgs, fet.vds)
elif sweep == 2:
    plot1 = FET.PlotIVVsT(make_array_4_sweep(t), make_array_4_sweep(vds))
fig_name = f"{experiment.filename[:-5]}.png"
fig_backup_name = fig_name + ".bak"
print("Done.")  # endregion

# region ----- Annealing -----
if annealing[0] is not None and settings.tc.address is not None:

    # region ----- Set temperature and wait for thermalization -----
    # set stage temperature controller setpoint
    tc.set_temperature(output=0, setpoint=annealing[0])
    # tc.set_temperature(output=1, setpoint=annealing[0]) if settings.tc.model == 0 else None

    # set thermalization time
    settling_time = annealing[1] * 3600
    print(f"Waiting for thermalization at {settling_time:04.1f} K...", end="")

    # allocate RAM
    ts = zeros(int(ceil(settling_time * settings.tc.sampling_freq)))
    stage = zeros_like(time)
    shield = zeros_like(time)

    # record data
    k = 0
    t0 = time.time()
    plot0.ax.set_xlim([0, settling_time])  # duration must be updated because the initial settling time is different from the regular time
    setpoint_line = plot0.ax.add_line(Line2D(xdata=array([0, settling_time]), ydata=array([annealing[0], annealing[0]]), color="grey", linewidth=1, linestyle="--"))  # add setpoint
    while time.time() - t0 <= settling_time:
        ts[k] = time.time() - t0
        stage[k] = tc.read_temperature("a")
        shield[k] = tc.read_temperature("b")
        plot0.ax.lines[0].set_data(ts[0:k+1], stage[0:k+1])
        plot0.ax.lines[1].set_data(ts[0:k+1], shield[0:k+1])
        plot0.ax.relim()
        plot0.ax.autoscale_view("y")
        plt.pause(1 / settings.tc.sampling_freq)
        k = k + 1

    # remove trailing zeros from saved data
    ts = ts[0:k]
    stage = stage[0:k]
    shield = shield[0:k]

    print("Done.")  # endregion

    # save figure to disc
    print("Saving thermalization figure to disc... ", end="")
    plot0.fig.savefig(fname=f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment} - annealing - {annealing[0]:.1f} K.png", format="png", dpi=300)
    print("Done.")

elif settings.tc.address is None:

    input(f"Set temperature to {annealing[0]:.1f} K, wait for {annealing[1]:.1f} h, then press Enter to continue...")

# endregion

for idx_t, val_t in enumerate(t):

    # region ----- Set temperature -----
    if settings.tc.address is not None:

        # region ----- Set temperature and wait for thermalization -----
        # set temperature controller setpoint
        tc.set_temperature(output=0, setpoint=val_t)
        tc.set_temperature(output=1, setpoint=val_t) if settings.tc.model == 0 else None

        # select thermalization time between initial and "regular" value
        print(f"Waiting for thermalization at {val_t:04.1f} K...", end="")
        if idx_t == 0:
            settling_time = settings.tc.settling_time_init
        else:
            settling_time = settings.tc.settling_time

        # record data
        k = 0
        t0 = time.time()
        if idx_t > 0:
            setpoint_line.remove()
        plot0.ax.set_xlim([0, settling_time])  # duration must be updated because the initial settling time is different from the regular time
        setpoint_line = plot0.ax.add_line(Line2D(xdata=array([0, settling_time]), ydata=array([val_t, val_t]), color="grey", linewidth=1, linestyle="--"))  # add setpoint
        while time.time() - t0 <= settling_time:
            fet.t[idx_t]["tt"].time[k] = time.time() - t0
            fet.t[idx_t]["tt"].stage[k] = tc.read_temperature("a")
            fet.t[idx_t]["tt"].shield[k] = tc.read_temperature("b")
            plot0.ax.lines[0].set_data(fet.t[idx_t]["tt"].time[0:k+1], fet.t[idx_t]["tt"].stage[0:k+1])
            plot0.ax.lines[1].set_data(fet.t[idx_t]["tt"].time[0:k+1], fet.t[idx_t]["tt"].shield[0:k+1])
            plot0.ax.relim()
            plot0.ax.autoscale_view("y")
            plt.pause(1 / settings.tc.sampling_freq)
            k = k + 1

        # remove trailing zeros from saved data
        fet.t[idx_t]["tt"].time = fet.t[idx_t]["tt"].time[0:k]
        fet.t[idx_t]["tt"].stage = fet.t[idx_t]["tt"].stage[0:k]
        fet.t[idx_t]["tt"].shield = fet.t[idx_t]["tt"].shield[0:k]

        print("Done.")  # endregion

        # save figure to disc
        print("Saving thermalization figure to disc... ", end="")
        plot0.fig.savefig(fname=f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment} - thermalization - {val_t:.1f} K.png", format="png", dpi=300)
        print("Done.")

    elif settings.tc.address is None:

        input(f"Set temperature to {val_t:04.1f} K, wait for thermalization, then press Enter to continue...")

    # endregion

    if sweep == 0:  # Transfer characteristic

        exit("Not yet implemented.")

        for idx_vds, val_vds in enumerate(fet.data[idx_t].vds):

            # region ----- Initialize Vgs and Vds -----
            val_vgs_ = adc.bin2voltage(adc.adw.Get_Par(51), bits=settings.adc.output_resolution) * settings.avv1.gain  # read current AO1 value
            val_vds_ = adc.bin2voltage(adc.adw.Get_Par(52), bits=settings.adc.output_resolution) * settings.avv2.gain  # read current AO2 value
            print(f"Setting:\n\t"
                  f"Vgs from {val_vgs_:.4f} V to {fet.data[idx_t].vgs[0]:.4f} V\n\t"
                  f"Vds from {val_vds_:.4f} V to {val_vds:.4f} V\n... ", end="")
            if val_vgs_ != vgs[0] or val_vds_ != val_vds:  # if AO1 or AO2 need to be initialized
                vgs_steps = int(ceil(abs(((val_vgs_ - fet.data[idx_t].vgs[0]) / settings.adc.sweep_step))))
                vds_steps = int(ceil(abs(((val_vds_ - val_vds) / settings.adc.sweep_rate))))
                n_steps = max(vds_steps, vgs_steps)
                data_vgs = linspace(val_vgs_, fet.data[idx_t].vgs[0], vgs_steps) / settings.avv1.gain  # generate voltage array
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
            bins_vgs = adc.voltage2bin(fet.data[idx_t].vgs / settings.avv1.gain)
            bins_vds = adc.voltage2bin(ones(len(fet.data[idx_t].vgs)) * val_vds / settings.avv2.gain)
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
                    fet.data[idx_: idx, idx_vds, 0] = fet.data[idx_t].vgs[idx_: idx]  # vgs
                    fet.data[idx_: idx, idx_vds, 1] = ai1  # igs
                    fet.data[idx_: idx, idx_vds, 2] = val_vds * ones(idx-idx_)  # vds
                    fet.data[idx_: idx, idx_vds, 3] = ai2  # ids
                    fet.data[idx_: idx, idx_vds, 4] = floor(linspace(idx_, idx, idx-idx_, False) / (len(fet.data[idx_t].vgs) / vgs[5]))  # store Vgs iteration
                    fet.data[idx_: idx, idx_vds, 5] = floor(idx_vds / (len(fet.data[idx_t].vds) / vds[5]))  # store Vds iteration
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
                if idx == len(fet.data[idx_t].vgs):
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
            plt.savefig(fname=fig_name, format="png", dpi=300)  # endregion

    if sweep == 1:  # Output characteristic

        exit("Not yet implemented.")

        for idx_vgs, val_vgs in enumerate(fet.data[idx_t].vgs):

            # region ----- Initialize Vgs and Vds -----
            val_vgs_ = adc.bin2voltage(adc.adw.Get_Par(51), bits=settings.adc.output_resolution) * settings.avv1.gain  # read current AO1 value
            val_vds_ = adc.bin2voltage(adc.adw.Get_Par(52), bits=settings.adc.output_resolution) * settings.avv2.gain  # read current AO2 value
            print(f"Setting:\n\t"
                  f"Vgs from {val_vgs_:.4f} V to {val_vgs:.4f} V\n\t"
                  f"Vds from {val_vds_:.4f} V to {fet.data[idx_t].vds[0]:.4f} V\n... ", end="")
            if val_vgs_ != val_vgs or val_vds_ != fet.data[idx_t].vds[0]:  # if AO1 or AO2 need to be initialized
                vgs_steps = int(ceil(abs(((val_vgs_ - val_vgs) / settings.adc.sweep_step))))
                vds_steps = int(ceil(abs(((val_vds_ - fet.data[idx_t].vds[0]) / settings.adc.sweep_step))))
                n_steps = max(vds_steps, vgs_steps)
                data_vgs = linspace(val_vgs_, val_vgs, n_steps) / settings.avv1.gain
                data_vds = linspace(val_vds_, fet.data[idx_t].vds[0], n_steps) / settings.avv2.gain
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
            bins_vgs = adc.voltage2bin(ones(len(fet.data[idx_t].vds)) * val_vgs / settings.avv1.gain, bits=settings.adc.output_resolution)
            bins_vds = adc.voltage2bin(fet.data[idx_t].vds / settings.avv2.gain, bits=settings.adc.output_resolution)
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
                    fet.data[idx_vgs, idx_: idx, 2] = fet.data[idx_t].vds[idx_: idx]  # vds
                    fet.data[idx_vgs, idx_: idx, 3] = ai2  # ids
                    fet.data[idx_vgs, idx_: idx, 4] = floor(idx_vgs / (len(fet.data[idx_t].vgs) / vgs[5]))  # store Vgs iteration
                    fet.data[idx_vgs, idx_: idx, 5] = floor(linspace(idx_, idx, idx-idx_, False) / (len(fet.data[idx_t].vds) / vds[5]))  # store Vds iteration
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
                if idx == len(fet.data[idx_t].vds):
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
            plt.savefig(fname=fig_name, format="png", dpi=300)  # endregion

    if sweep == 2:  # IV

        # region ----- Initialize Vds -----
        val_vds_ = adc.bin2voltage(adc.adw.Get_Par(52), bits=settings.adc.output_resolution) * settings.avv2.gain  # read current AO2 value
        print(f"Setting:\n\t"
              f"Vds from {val_vds_:.4f} V to {fet.data[idx_t].vds[0]:.4f} V\n... ", end="")
        if val_vds_ != fet.data[idx_t].vds[0]:  # if AO1 or AO2 need to be initialized
            vds_steps = int(ceil(abs(val_vds_ - fet.data[idx_t].vds[0]) / settings.adc.sweep_step))
            data_vds = linspace(val_vds_, fet.data[idx_t].vds[0], vds_steps) / settings.avv2.gain
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
        bins_vds = adc.voltage2bin(fet.data[idx_t].vds / settings.avv2.gain, bits=settings.adc.output_resolution)
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
                fet.data[idx_t].data[0, idx_: idx, 2] = fet.data[idx_t].vds[idx_: idx]  # vds
                fet.data[idx_t].data[0, idx_: idx, 3] = ai2  # ids
                fet.data[idx_t].data[0, idx_: idx, 5] = floor(linspace(idx_, idx, idx-idx_, False) / (len(fet.data[idx_t].vds) / vds[5]))  # store Vds iteration
                # plot
                plot1.ax0.lines[idx_t].set_data(fet.data[idx_t].data[0, 0: idx, 2], fet.data[idx_t].data[0, 0: idx, 3])
                plot1.ax0.relim()
                plot1.ax0.autoscale_view(scalex=False, scaley=True)
                plot1.ax1.lines[idx_t].set_data(fet.data[idx_t].data[0, 0: idx, 2], log10(abs(fet.data[idx_t].data[0, 0: idx, 3])))
                plot1.ax1.relim()
                plot1.ax1.autoscale_view(scalex=False, scaley=True)
                idx_ = idx
            plt.pause(0.1)
            if idx == len(fet.data[idx_t].vds):
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
input("Measurement complete. Press Enter to terminate.")
exit()
