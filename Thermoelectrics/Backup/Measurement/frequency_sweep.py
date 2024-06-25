# region ----- Import packages -----
import srs_sr830
import srs_srcs580
import adwin
import lakeshore_tc336
import oxford_mercury_itc
import pyvisa
import os
from numpy import mean, std, arctan, rad2deg, ctypeslib
import pickle
from Objects.Backup.measurement_objects import *
from Objects.Backup.plot_objects import *
from Utilities.signal_processing import *
import time
import datetime
# endregion

#######################################################################
#   Author:         Davide Beretta
#   Date:           28.07.2021
#   Description:    TE-FET: frequency sweep (for Stanford and ADwin Gold II)
#
#   Instrumentation settings are remotely set and controlled only if
#   the user provides the interface address.
#
#   ADwin Analog Output - Analog Input configuration
#   AO1: thermoresistance 1 current
#   AO2: thermoresistance 2 current
#   AI1: thermoresistance 1 dc
#   AI2: thermoresistance 2 dc
#   AI3: thermoresistance 1 x
#   AI4: thermoresistance 2 x
#   AI5: thermoresistance 1 y
#   AI6: thermoresistance 2 y
#   AI7: DUT x (when measuring low impedance DUTs, otherwise not connected)
#   AI8: DUT y (when measuring low impedance DUTs, otherwise not connected)

#   #######################################################################

# region ----- Measurement options -----
experiment = Experiment()
experiment.experiment = "frequency sweep"
experiment.main = r"E:\Samples\dabe"
experiment.date = datetime.datetime.now()
experiment.chip = "teps02"
experiment.device = "d2"
experiment.filename = f"{experiment.chip} - {experiment.device} - {experiment.experiment}.data"
experiment.backupname = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
thermometer = 1                         # [string or int] select the thermometer to calibrate: "1" (int), "2" (int), or "both" (string)
heater = 1                              # [int] select heater in use (it has no practical effect on the code)
t = array([200])                        # [1D array] temperatures (in K).
i_h = array([0e-3, 1e-3, 2e-3, 3e-3, 4e-3, 5e-3])   # [1D array] heater current (in A).
i_th = linspace(0, 50e-6, 51)           # [1D array] "forward" thermometer current for iv (in A).
i_th = concatenate((i_th[:-1], flip(i_th)[:-1], (-i_th)[:-1], flip(-i_th)[:-1]))
i_th_ex = 50e-6                         # [float] thermometer excitation current (in A).
i_th_ex_steps = 50                     # [int] number of thermometer excitation current steps.
f = logspace(0, 3, 31)                 # [1D array] frequencies (in Hz)
heater_settling_time = 60 * 3           # [float] settling time (in s) after setting heater current
# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------

# region ----- Settings ------
settings = EmptyClass()
# ----- tc settings -----
settings.__setattr__("tc", EmptyClass())
settings.tc.model = 1                       # [int] select tc model (0: lakeshore 336, 1: oxford mercury itc)
settings.tc.address = "ASRL8::INSTR"        # [string] address of temperature controller
settings.tc.t_switch = 50                   # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium"
settings.tc.sampling_freq = 1               # [int] temperature sampling frequency (in Hz)
settings.tc.settling_time = 60 * 1         # [float] cryostat thermalization time (in s).
settings.tc.settling_time_init = 1 * 1 * 60    # [float] cryostat initial thermalization time (in s).
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
settings.adc.vt_settling_time = 60 * 0.1      # [float] measurement time (in s). The number of samples is: vt_time / (nplc / line_freq)
settings.adc.vt_measurement_time = 60 * 0.1   # [float] measurement time (in s). The number of samples is: vt_time / (nplc / line_freq)
# ----- Thermometer 1 -----
# ----- src1 settings -----
settings.__setattr__("src1", EmptyClass())
settings.src1.model = 1                     # [int] select src1 model (0: srs cs580, 1: tu delft IVa)
settings.src1.address = None  #"ASRL10::INSTR"  #  [string] address. Set None if not connected to PC
settings.src1.gain = 100e-6                  # [float] gain (in A/V)
settings.src1.isolation = "float"           # [string] isolation
settings.src1.shield = "return"             # [string] shield
settings.src1.compliance = 1                # [float] compliance (in V)
settings.src1.response = None  #"slow"      # [string] response ("slow" adds a 470 pF to the output. The response time of the circuit is R * 470 pF)
settings.src1.delay = 0.1                   # [string] current source settling time (in s). Used when unit is controlled via Serial.
settings.src1.rate = 10e-6                  # [float] current sweep rate (in A/s). Used in current sweep when unit is controlled via Serial.
settings.src1.step = 1e-6                   # [float] current step (in A). Used in current sweep when unit is controlled via Serial.
# ----- avv1 settings -----
settings.__setattr__("avv1", EmptyClass())
settings.avv1.model = 1                     # [int] select amplifier model (0: srs sr560, 1: tu delft IVa, 2: tu delft M2m)
settings.avv1.address = None                # [string] address. Set None if not connected to PC
settings.avv1.gain = 1e3                    # [float] gain (in V/V)
settings.avv1.lpf = None  #100                     # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.coupling = None  # "dc"               # [string] coupling (ac or dc)
# ----- lock-in1 (thermomter 1 and heater) settings -----
# When using external adc, Output = (signal/sensitivity - offset) x Expand x 10 V
# Set offset = 0 and Expand = 1 (default)
settings.__setattr__("lockin1", EmptyClass())
settings.lockin1.address = "GPIB0::1::INSTR"  # [string] address of lockin 1
settings.lockin1.reference = "internal"     # [string] reference source ("internal" or "external")
settings.lockin1.freq = 1                   # [float] excitation current frequency (in Hz)
settings.lockin1.shield = "float"           # [string] shield ca nbe floating or shorted
settings.lockin1.coupling = "ac"            # [string] coupling can be AC (add a HPF at 0.16 Hz) or DC
settings.lockin1.time = 3                   # [float] integration time
settings.lockin1.filter = "24 dB/oct"       # [string] filter
settings.lockin1.input = "a"                # [string] input can be single ended ("a") or differential ("a-b")
settings.lockin1.sensitivity = 100e-3       # [string] sensitivity (in V). If input signal is current, sensitivity (in A) = sensitivity (in V) * 1e-6 A/V
settings.lockin1.harmonic = 2               # [int] demodulated harmonic
settings.lockin1.reserve = "normal"         # [string]
# ----- Thermometer 2 -----
# ----- src2 settings -----
settings.__setattr__("src2", EmptyClass())
settings.src2.model = settings.src1.model   # [int] select src1 model (0: srs cs580, 1: tu delft XXX)
settings.src2.address = None  #"ASRL11::INSTR"     # [string] address. Set None if not connected to PC
settings.src2.gain = settings.src1.gain     # [float] gain (in A/V)
settings.src2.isolation = settings.src1.isolation  # [string] isolation
settings.src2.shield = settings.src1.shield  # [string] shield
settings.src2.compliance = settings.src1.compliance  # [float] compliance (in V))
settings.src2.response = settings.src1.response  # [string] response ("slow" adds a 470 pF to the output. The response time of the circuit is R * 470 pF)
settings.src2.delay = settings.src1.delay   # [string] current source settling time (in s)
settings.src2.step = settings.src1.step     # [float] current step (in A). Used in current sweep.
# ----- avv2 settings -----
settings.__setattr__("avv2", EmptyClass())
settings.avv2.model = settings.avv1.model   # [int] select amplifier model (0: srs sr560, 1: tu delft M2m)
settings.avv2.address = settings.avv1.address  # [string] address. Set None if not connected to PC
settings.avv2.gain = settings.avv1.gain     # [float] gain (in V/V)
settings.avv2.lpf = settings.avv1.lpf       # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.hpf = settings.avv1.hpf       # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.coupling = settings.avv1.coupling  # [string] coupling (ac or dc)
# ----- lock-in2 settings -----
settings.__setattr__("lockin2", EmptyClass())
settings.lockin2.address = "GPIB0::2::INSTR"  # [string] address of lockin 2
settings.lockin2.reference = "external"     # [string] reference source ("internal" or "external")
settings.lockin2.freq = settings.lockin1.freq  # [float] excitation current frequency (in Hz)
settings.lockin2.shield = settings.lockin1.shield  # [string] shield ca nbe floating or shorted
settings.lockin2.coupling = settings.lockin1.coupling  # [string] coupling can be AC (add a HPF at 0.16 Hz) or DC
settings.lockin2.time = settings.lockin1.time  # [float] integration time
settings.lockin2.filter = settings.lockin1.filter  # [string] filter
settings.lockin2.input = settings.lockin1.input  # [string] input can be single ended ("a") or differential ("a-b")
settings.lockin2.sensitivity = settings.lockin1.sensitivity  # [string] sensitivity (in V). If input signal is current, sensitivity (in A) = sensitivity (in V) * 1e-6 A/V
settings.lockin2.harmonic = settings.lockin1.harmonic  # [int] demodulated harmonic
settings.lockin2.reserve = settings.lockin1.reserve  # [string] reserve
# ----- Heater -----
# ----- src3 (heater) settings -----
settings.__setattr__("src3", EmptyClass())
settings.src3.model = 0                     # [int] select src1 model (0: srs cs580, 1: tu delft XXX)
settings.src3.address = "ASRL11::INSTR"                # [string] address. Set None if not connected to PC
settings.src3.gain = 10e-3                  # [float] gain (in A/V)
settings.src3.isolation = "float"           # [string] isolation
settings.src3.shield = "return"             # [string] shield
settings.src3.compliance = 7               # [float] compliance (in V)
settings.src3.response = "slow"             # [string] response
settings.src3.delay = 0.1                   # [string] current source settling time (in s). Used when unit is controlled via Serial.
settings.src3.rate = 10e-6                  # [float] current sweep rate (in A/s). Used in current sweep when unit is controlled via Serial.
settings.src3.step = 1e-6                   # [float] current step (in A). Used in current sweep when unit is controlled via Serial.
# ----------
experiment.settings = settings
# endregion

# region ----- Message to the user -----
print(f"""\n***** Measurement summary *****
chip: {experiment.chip}
device: {experiment.device}
thermometer(s): {thermometer}
heater: {heater}
temperatures: {"".join([f"{x:.1f} K, " for x in t])}
heater current: {"".join([f"{1e3*x:.1f} mA, " for x in i_h])}
frequency range: {f[0]} Hz - {f[-1]} Hz""")
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
    # set analog input and output in use,
    if thermometer == 1 or thermometer == "both":
        adc.adw.Set_Par(1, 1)  # analog input 1 (0: off, 1: on)
        adc.adw.Set_Par(3, 1)  # analog input 3 (0: off, 1: on)
        adc.adw.Set_Par(5, 1)  # analog input 5 (0: off, 1: on)
        adc.adw.Set_Par(21, 1)  # analog output 1 (0: off, 1: on)
    if thermometer == 2 or thermometer == "both":
        adc.adw.Set_Par(2, 1)  # analog input 2 (0: off, 1: on)
        adc.adw.Set_Par(4, 1)  # analog input 4 (0: off, 1: on)
        adc.adw.Set_Par(6, 1)  # analog input 6 (0: off, 1: on)
        adc.adw.Set_Par(22, 1)  # analog output 2 (0: off, 1: on)
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

if settings.src3.address is not None and settings.src3.model == 0:
    src3 = srs_srcs580.srcs580(visa=rm.open_resource(settings.src3.address))
    src3.configure(settings.src3.gain, settings.src3.response, settings.src3.shield,
                   settings.src3.isolation, "off", "on", settings.src3.compliance)
    print(f"Current source 3: {src3.read_model()} drivers loaded and configured.")

if settings.lockin1.address is not None:
    lockin1 = srs_sr830.sr830(visa=rm.open_resource(settings.lockin1.address))
    lockin1.configure(settings.lockin1.reference, 0, settings.lockin1.freq, settings.lockin1.harmonic,
                      settings.lockin1.input, settings.lockin1.shield, settings.lockin1.coupling,
                      settings.lockin1.sensitivity, settings.lockin1.reserve, settings.lockin1.time,
                      settings.lockin1.filter)
    print(f"Lockin 1: {lockin1.read_model()} drivers loaded and configured.")

if settings.lockin2.address is not None:
    lockin2 = srs_sr830.sr830(visa=rm.open_resource(settings.lockin2.address))
    lockin2.configure(settings.lockin2.reference, 0, settings.lockin2.freq, settings.lockin2.harmonic,
                      settings.lockin2.input, settings.lockin2.shield, settings.lockin2.coupling,
                      settings.lockin2.sensitivity, settings.lockin2.reserve, settings.lockin2.time,
                      settings.lockin2.filter)
    print(f"Lockin 2: {lockin2.read_model()} drivers loaded and configured.")
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
data = TemperatureFrequencySweep(heater, thermometer, t, i_h, f, settings)
print("Done.")
# endregion

# region ----- Initialize figures ------
print("Initializing figure... ", end="")
if settings.tc.address is not None:
    plot0 = PlotObsT(["stage", "shield"], settings.tc.settling_time)
plot1 = PlotSweepF(t, f, i_h)
plt.show(block=False)
plt.pause(.1)
print("Done.")  # endregion

input("Unground the device, then press Enter to start measurement...")
current_input_state = False  # flag for heater source when V < 0.004

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
            data.t[idx_t]["tt"].time[k] = time.time() - t0
            data.t[idx_t]["tt"].stage[k] = tc.read_temperature("a")
            data.t[idx_t]["tt"].shield[k] = tc.read_temperature("b")
            plot0.ax.lines[0].set_data(data.t[idx_t]["tt"].time[0:k + 1], data.t[idx_t]["tt"].stage[0:k + 1])
            plot0.ax.lines[1].set_data(data.t[idx_t]["tt"].time[0:k + 1], data.t[idx_t]["tt"].shield[0:k + 1])
            plot0.ax.relim()
            plot0.ax.autoscale_view("y")
            plt.pause(1 / settings.tc.sampling_freq)
            k = k + 1

        # remove trailing zeros from saved data
        data.t[idx_t]["tt"].time = data.t[idx_t]["tt"].time[0:k]
        data.t[idx_t]["tt"].stage = data.t[idx_t]["tt"].stage[0:k]
        data.t[idx_t]["tt"].shield = data.t[idx_t]["tt"].shield[0:k]

        print("Done.")  # endregion

        # save figure to disc
        print("Saving thermalization figure to disc... ", end="")
        plot0.fig.savefig(fname=f"thermalization - {val_t:04.1f} K.png", format="png")
        print("Done.")

    elif settings.tc.address is None:

        input(f"Set temperature to {val_t:04.1f} K, wait for thermalization, then press Enter to continue...")

    # endregion

    # region ----- Ramp up thermometer(s) current -----
    print(f"Ramping up thermometer(s) current from 0 uA to {1e6 * i_th_ex:04.1f} uA... ", end="")
    temp = linspace(0, i_th_ex, i_th_ex_steps)
    if thermometer == 1 or thermometer == "both":
        adc.adw.Set_Par(41, len(temp))  # set length of v1 array
        adc.adw.SetData_Long(list(adc.voltage2bin(temp / settings.src1.gain, bits=settings.adc.output_resolution)), 21, 1, len(temp))  # set ao1 data
    if thermometer == 2 or thermometer == "both":
        adc.adw.Set_Par(42, len(temp))  # set length of v1 array
        adc.adw.SetData_Long(list(adc.voltage2bin(temp / settings.src2.gain, bits=settings.adc.output_resolution)), 22, 1, len(temp))  # set ao2 data
    adc.adw.Start_Process(4)
    while adc.adw.Process_Status(4) == 1:
        plt.pause(1e-3)
    print("Done.")  # endregion ----------------------------------------------

    for idx_i_h, val_i_h in enumerate(i_h):

        # region ----- Ramp up heater current -----
        val_i_h_ = 0 if idx_i_h == 0 else i_h[idx_i_h - 1]

        # check heater source state
        if amplitude2rms(val_i_h / settings.src3.gain) < 0.004:
            if current_input_state is True:
                if settings.src3.address is not None:
                    src3.operation(input_state="off", output_state="on")
                    current_input_state = False
                else:
                    input("Set 'src3' input = off and output = on, then press Enter to continue.")
                    current_input_state = False
            else:
                pass
        else:
            if current_input_state is True:
                pass
            else:
                if settings.src3.address is not None:
                    src3.operation(input_state="on", output_state="on")
                else:
                    input("Set 'src3' input = on and output = on, then press Enter to continue.")
                    current_input_state = True  # to skip next iteration src3 settings

        # # check lockin 2 reference
        # if amplitude2rms(val_i_h / settings.src3.gain) < 0.1:
        #     if settings.lockin2.reference == "external":
        #         if settings.lockin2.address is not None:
        #             lockin2.set_reference("internal")
        #             lockin2.set_frequency(settings.lockin1.freq)
        #             settings.lockin2.address = "internal"
        #         else:
        #             input(f"Set lockin 2 reference to 'internal' and lockin 2 frequency to {settings.lockin1.freq:.3f} Hz, then press Enter to continue.")
        #             settings.lockin2.address = "internal"
        #     elif settings.lockin2.reference == "internal":
        #         pass
        # else:
        #     if settings.lockin2.reference == "external":
        #         pass
        #     elif settings.lockin2.reference == "internal":
        #         if settings.lockin2.address is not None:
        #             lockin2.set_reference("external")
        #             settings.lockin2.address = "external"
        #         else:
        #             input(f"Set lockin 2 reference to 'external', then press Enter to continue.")
        #             settings.lockin2.address = "external"

        if settings.lockin1.address is not None:
            print(f"Ramping up heater current from {1e3 * val_i_h_:.1f} mA to {1e3 * val_i_h:.1f} mA... ", end="")
            lockin1.sweep_v(amplitude2rms(val_i_h_ / settings.src3.gain), amplitude2rms(val_i_h / settings.src3.gain))
            print("Done.")
        else:
            input(f"Set lockin 1 output to {amplitude2rms(val_i_h / settings.src3.gain):04.1f} Vrms, then press Enter to continue.")
        # endregion

        # region ----- Wait for steady state -----
        t0 = time.time()
        print("Waiting for steady state... ", end="")
        while time.time() - t0 <= heater_settling_time:
            pass
        print("Done.")  # endregion

        # for plotting purposes
        if thermometer == 1 or thermometer == "both":
            rho1 = zeros(len(f))
            phi1 = zeros(len(f))

        if thermometer == 2 or thermometer == "both":
            rho2 = zeros(len(f))
            phi2 = zeros(len(f))

        for idx_f, val_f in enumerate(f):

            # region ----- Set settling and measurement time, and samples numbers -----
            print("Setting settling time and measurement time... ", end="")
            if val_f < 10:
                if thermometer == 1 or thermometer == "both":
                    lockin1.set_integration_time(3)
                if thermometer == 2 or thermometer == "both":
                    lockin2.set_integration_time(3)
                settling_time = 3 * 10 * 3
                measurement_time = 3 * 10
            elif (val_f >= 10) and (val_f < 100):
                if thermometer == 1 or thermometer == "both":
                    lockin1.set_integration_time(1)
                if thermometer == 2 or thermometer == "both":
                    lockin2.set_integration_time(1)
                settling_time = 1 * 10 * 3
                measurement_time = 1 * 10
            elif val_f >= 100:
                if thermometer == 1 or thermometer == "both":
                    lockin1.set_integration_time(100e-3)
                if thermometer == 2 or thermometer == "both":
                    lockin2.set_integration_time(100e-3)
                settling_time = 1 * 10 * 3
                measurement_time = 0.1 * 10

            vt_samples = int(ceil((settling_time + measurement_time) / (settings.adc.nplc / settings.adc.line_freq)))
            vt_samples2avg = int(ceil(measurement_time / (settings.adc.nplc / settings.adc.line_freq)))
            adc.adw.Set_Par(71, vt_samples)
            print("Done.")  # endregion

            # region ----- Set Lockin frequency -----
            print(f"Setting lockin frequency to {val_f:.1f} Hz... ", end="")
            lockin1.set_frequency(val_f)
            print("Done")  # endregion

            # region ----- Measure oscillations -----
            print("Measuring oscillations... ", end="")
            adc.adw.Start_Process(2)
            while adc.process_status(2) is True:
                plt.pause(0.01)
            print("Done.")  # endregion

            # region ----- Read data from ADC -----
            print("Reading data from ADC... ", end="")
            # adc_time = adc.adw.GetData_Float(9, 1, vt_samples)
            adc_time = idx2time(linspace(0, vt_samples, vt_samples, endpoint=False), settings.adc.nplc, settings.adc.line_freq)

            if thermometer == 1 or thermometer == "both":
                # read from adc
                ai1 = ctypeslib.as_array(adc.adw.GetData_Float(1, 1, vt_samples))
                ai3 = ctypeslib.as_array(adc.adw.GetData_Float(3, 1, vt_samples))
                ai5 = ctypeslib.as_array(adc.adw.GetData_Float(5, 1, vt_samples))
                # convert data
                v1 = adc.bin2voltage(ai1, bits=settings.adc.input_resolution) / settings.avv1.gain / i_th_ex  # raw
                v3 = adc.bin2voltage(ai3, bits=settings.adc.input_resolution) * settings.lockin1.sensitivity / 10 / settings.avv1.gain / i_th_ex  # x
                v5 = adc.bin2voltage(ai5, bits=settings.adc.input_resolution) * settings.lockin1.sensitivity / 10 / settings.avv1.gain / i_th_ex  # y
                rho1[idx_f] = mean(v3[-vt_samples2avg:] ** 2 + v5[-vt_samples2avg:] ** 2)
                phi1[idx_f] = mean(rad2deg(arctan(v5[-vt_samples2avg:] / v3[-vt_samples2avg:])))
                # store converted data in data object
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].time = adc_time
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].raw = v1
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].raw_avg = mean(v1[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].raw_stddev = std(v1[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].x = v3
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].x_avg = mean(v3[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].x_stddev = std(v3[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].y = v5
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].y_avg = mean(v5[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].y_stddev = std(v5[-vt_samples2avg:])

            if thermometer == 2 or thermometer == "both":
                ai2 = ctypeslib.as_array(adc.adw.GetData_Float(2, 1, vt_samples))
                ai4 = ctypeslib.as_array(adc.adw.GetData_Float(4, 1, vt_samples))
                ai6 = ctypeslib.as_array(adc.adw.GetData_Float(6, 1, vt_samples))
                # convert data
                v2 = adc.bin2voltage(ai2, bits=settings.adc.input_resolution) / settings.avv2.gain / i_th_ex  # raw
                v4 = adc.bin2voltage(ai4, bits=settings.adc.input_resolution) * settings.lockin2.sensitivity / 10 / settings.avv2.gain / i_th_ex  # x
                v6 = adc.bin2voltage(ai6, bits=settings.adc.input_resolution) * settings.lockin2.sensitivity / 10 / settings.avv2.gain / i_th_ex  # y
                rho2[idx_f] = mean(v4[-vt_samples2avg:] ** 2 + v6[-vt_samples2avg:] ** 2)
                phi2[idx_f] = mean(rad2deg(arctan(v6[-vt_samples2avg:] / v4[-vt_samples2avg:])))
                # store converted data in data object
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].time = adc_time
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].raw = v2
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].raw_avg = mean(v2[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].raw_stddev = std(v2[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].x = v4
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].x_avg = mean(v4[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].x_stddev = std(v4[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].y = v6
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].y_avg = mean(v6[-vt_samples2avg:])
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].y_stddev = std(v6[-vt_samples2avg:])
            print("Done.")  # endregion

            # region ----- Update plot -----
            print("Updating plot... ", end="")

            if thermometer == 1 or thermometer == "both":

                plot1.axx.lines[2 * idx_i_h].set_data(f[0:idx_f+1], [data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][k]["drt1"].x_avg for k in range(idx_f+1)])
                plot1.axy.lines[2 * idx_i_h].set_data(f[0:idx_f+1], [data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][k]["drt1"].y_avg for k in range(idx_f+1)])

                plot1.axr.lines[2 * idx_i_h].set_data(f[0:idx_f+1], rho1[0:idx_f+1])
                plot1.axp.lines[2 * idx_i_h].set_data(f[0:idx_f+1], phi1[0:idx_f+1])

            if thermometer == 2 or thermometer == "both":

                plot1.axx.lines[2 * idx_i_h + 1].set_data(f[0:idx_f+1], [data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][k]["drt2"].x_avg for k in range(idx_f+1)])
                plot1.axy.lines[2 * idx_i_h + 1].set_data(f[0:idx_f+1], [data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][k]["drt2"].y_avg for k in range(idx_f+1)])

                plot1.axr.lines[2 * idx_i_h + 1].set_data(f[0:idx_f+1], rho2[0:idx_f+1])
                plot1.axp.lines[2 * idx_i_h + 1].set_data(f[0:idx_f+1], phi2[0:idx_f+1])

            plot1.axx.relim()
            plot1.axx.autoscale_view("y")
            plot1.axy.relim()
            plot1.axy.autoscale_view("y")
            plot1.axr.relim()
            plot1.axr.autoscale_view("y")
            plot1.axp.relim()
            plot1.axp.autoscale_view("y")

            plt.pause(0.001)
            print("Done.")  # endregion

    # region ----- Ramp down thermometer(s) current -----
    print(f"Ramping down thermometer(s) current to 0 uA... ", end="")
    temp = linspace(i_th_ex, 0, i_th_ex_steps)
    if thermometer == 1 or thermometer == "both":
        adc.adw.Set_Par(41, len(temp))  # set length of v1 array
        adc.adw.SetData_Long(list(adc.voltage2bin(temp / settings.src1.gain, bits=settings.adc.output_resolution)), 21, 1, len(temp))  # set ao1 data
    if thermometer == 2 or thermometer == "both":
        adc.adw.Set_Par(42, len(temp))  # set length of v1 array
        adc.adw.SetData_Long(list(adc.voltage2bin(temp / settings.src2.gain, bits=settings.adc.output_resolution)), 22, 1, len(temp))  # set ao2 data
    adc.adw.Start_Process(4)
    while adc.adw.Process_Status(4) == 1:
        plt.pause(1e-3)
    print("Done.")  # endregion ----------------------------------------------

    # region ----- Ramp down heater current -----
    if settings.lockin1.address is not None:
        print(f"Ramping down heater current from {1e3 * val_i_h:.1f} mA to {0:.1f} mA... ", end="")
        lockin1.sweep_v(amplitude2rms(val_i_h / settings.src3.gain), 0)
        print("Done.")
    else:
        input(f"Set lockin 1 output to 0 V, then press Enter to continue.")
    if settings.src3.address is not None:
        src3.set_output_state("off")
    # endregion

    # region ----- Save data to disc -----
    print("Saving data to disc... ", end="")
    experiment.data = data
    if os.path.exists(experiment.filename):
        if os.path.exists(experiment.backupname):
            os.remove(experiment.backupname)
        os.rename(experiment.filename, experiment.backupname)
    with open(experiment.filename, "wb") as file:
        pickle.dump(experiment, file)
    print("Done.")
    print("Saving figure to disc... ", end="")
    plot1.fig.savefig(fname=f"{experiment.experiment} - {val_t:04.1f} K - {1e3*val_i_h:04.1f} mA - {f[0]:.1f} Hz - {f[-1]:04.1f} Hz.png", format="png")
    print("Done.")
    # endregion

input("Measurement complete. Ground the device then press Enter to terminate.")
plt.plot()