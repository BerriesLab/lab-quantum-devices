# region ----- Import packages -----
import srs_sr830
import srs_srcs580
import adwin
import lakeshore_tc336
import oxford_mercury_itc
import pyvisa
import os
from numpy import mean, std, arctan, rad2deg, ctypeslib, logspace
import pickle
from Objects.measurement import *
from Utilities.signal_processing import *
import time
import datetime
# endregion

"""
#######################################################################
   Author:         Davide Beretta
   Date:           14.02.2022
   Description:    TE-FET: frequency sweep (for Stanford and ADwin Gold II)

   Instrumentation settings are remotely set and controlled only if
   the user provides the interface address.

   ADwin Analog Output - Analog Input configuration
   AO1: thermoresistance 1 current
   AO2: thermoresistance 2 current
   AI1: thermoresistance 1 dc
   AI2: thermoresistance 2 dc
   AI3: thermoresistance 1 x
   AI4: thermoresistance 2 x
   AI5: thermoresistance 1 y
   AI6: thermoresistance 2 y
   #######################################################################
"""

# region ----- measurement options -----
experiment = Experiment()
experiment.experiment_name = "calibration vs frequency"
experiment.main_path = r"E:\Samples\dabe"
experiment.date = datetime.datetime.now()
experiment.chip = "sample simulator"
experiment.device = "tester"
experiment.filename = f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment_name}.data"
experiment.backup_filename = f"{experiment.filename}.bak"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
thermometer = 2  # [int] select the thermometer to calibrate {0: both, 1: th1, 2: th2}
heater = 1  # [int] select heater in use (it has no practical effect on the code)
t = array([295])  # [1D array] temperatures (in K).
i_h = array([0e-3, 1e-3])  # [1D array] heater current (in A).
i_th = linspace(0, 50e-6, 51)  # [1D array] "forward" thermometer current for iv (in A).
i_th = concatenate((i_th[:-1], flip(i_th)[:-1], (-i_th)[:-1], flip(-i_th)[:-1]))
i_th_ex = 50e-6  # [float] thermometer excitation current (in A).
i_th_ex_steps = 50  # [int] number of thermometer excitation current steps.
f = logspace(1, 4, 3)  # [1D array] frequencies (in Hz)
heater_settling_time = 0.01*60 * 3  # [float] settling time (in s) after setting heater current
# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------

# region ----- settings ------
settings = EmptyClass()
# ----- tc settings -----
settings.__setattr__("tc", EmptyClass())
settings.tc.model = 1                       # [int] select tc model (0: lakeshore 336, 1: oxford mercury itc)
settings.tc.address = "ASRL8::INSTR"        # [string] address of temperature controller
settings.tc.t_switch = 50                   # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium"
settings.tc.sampling_freq = 1               # [int] temperature sampling frequency (in Hz)
settings.tc.settling_time = 0.1*60 * 1          # [float] cryostat thermalization time (in s).
settings.tc.settling_time_init = 0.1 * 1 * 60    # [float] cryostat initial thermalization time (in s).
# ----- adc settings -----
settings.__setattr__("adc", EmptyClass())
settings.adc.model = 0                      # [int] select adc model (0: ADwinGoldII gold ii)
settings.adc.input_resolution = 18          # [int] input resolution (in bit)
settings.adc.output_resolution = 16         # [int] output resolution (in bit)
settings.adc.clock_freq = 300e6             # [int] clock frequency (in Hz)
settings.adc.line_freq = 50                 # [int] line frequency (in Hz)
settings.adc.scan_rate = 40e3                # [int] frequency at which the script is executed (in Hz)
settings.adc.n_plc = 10                      # [float] number of power line cycles
settings.adc.iv_settling_time = 0.1         # [float] settling time (in s) before recording data
settings.adc.vt_settling_time = 60 * 0.1      # [float] measurement time (in s). The number of samples is: vt_time / (n_plc / line_freq)
settings.adc.vt_measurement_time = 60 * 0.1   # [float] measurement time (in s). The number of samples is: vt_time / (n_plc / line_freq)
# ----- Thermometer 1 -----
# ----- src1 settings -----
settings.__setattr__("src1", EmptyClass())
settings.src1.model = 1                     # [int] select src1 model (0: srs cs580, 1: tu delft IVa)
settings.src1.address = None                # [string] address. Set None if not connected to PC
settings.src1.gain = 100e-6                 # [float] gain (in A/V)
settings.src1.isolation = "float"           # [string] isolation
settings.src1.shield = "return"             # [string] shield
settings.src1.compliance = 1                # [float] compliance (in V)
settings.src1.response = None               # [string] response ("slow" adds a 470 pF to the output. The response time of the circuit is R * 470 pF)
settings.src1.delay = 0.1                   # [string] current source settling time (in s). Used when unit is controlled via Serial.
settings.src1.rate = 10e-6                  # [float] current sweep rate (in A/s). Used in current sweep when unit is controlled via Serial.
settings.src1.step = 1e-6                   # [float] current step (in A). Used in current sweep when unit is controlled via Serial.
# ----- avv1 settings -----
settings.__setattr__("avv1", EmptyClass())
settings.avv1.model = 1                     # [int] select amplifier model (0: srs sr560, 1: tu delft IVa, 2: tu delft M2m)
settings.avv1.address = None                # [string] address. Set None if not connected to PC
settings.avv1.gain = 1e2                    # [float] gain (in V/V)
settings.avv1.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.coupling = None               # [string] coupling (ac or dc)
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
settings.src2.address = None                # [string] address. Set None if not connected to PC
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
settings.src3.address = "ASRL5::INSTR"                # [string] address. Set None if not connected to PC
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
print(f"""\n***** measurement summary *****
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
    routines_dir = "C:/Python scripts/lab-scripts/instrumentation_library/adwin_gold_ii_routines"  # directory of routines files
    adc = adwin.ADwinGoldII(boot_dir, routines_dir)
    adc.adw.Load_Process(routines_dir + "/sweep_ao1_read_ai1.TB1")  # Load sweep AO1 and read AI1
    adc.adw.Load_Process(routines_dir + "/sweep_ao2_read_ai2.TB2")  # Load sweep AO2 and read AI2
    adc.adw.Load_Process(routines_dir + "/sweep_ao1-2_read_ai1-2.TB3")  # Load sweep AO2 and read AI2
    adc.adw.Load_Process(routines_dir + "/read_ai1-10.TB4")  # Load read AI1-10
    adc.adw.Load_Process(routines_dir + "/sweep_ao1.TB5")  # Load sweep AO1-2
    adc.adw.Load_Process(routines_dir + "/sweep_ao2.TB6")  # Load sweep AO1-2
    adc.adw.Load_Process(routines_dir + "/sweep_ao1-2.TB7")  # Load sweep AO1-2
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
    # number of samples of a time-dependent measurement = time / n_plc * line_freq
    adc.adw.Set_Par(71, int(ceil((settings.adc.vt_settling_time + settings.adc.vt_measurement_time) / (settings.adc.n_plc / settings.adc.line_freq))))
    # set initial values of AO1 and AO2
    adc.adw.Set_Par(51, adc.voltage2bin(0, bits=settings.adc.output_resolution))
    adc.adw.Set_Par(52, adc.voltage2bin(0, bits=settings.adc.output_resolution))
    print(f"ADC-DAC: ADwin Gold II drivers loaded and configured.")

if settings.tc.address is not None and settings.tc.model == 0:
    tc = lakeshore_tc336.Lakeshore336(visa=rm.open_resource(settings.tc.address))
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
print("\n***** measurement log *****")
path = f"{experiment.main_path}\\{experiment.chip}\\{experiment.device}\\{experiment.experiment_name}\\"
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
data = Thermoelectrics.TemperatureVsFrequency(heater, thermometer, t, i_h, f, settings)
print("Done.")
# endregion

# region ----- Initialize figures ------
print("Initializing figure... ", end="")
if settings.tc.address is not None:
    plot0 = PlotObsT(["stage", "shield"], settings.tc.settling_time)
plot1 = Thermoelectrics.PlotTemperatureVsFrequency(t, f, i_h)
plot2 = PlotObsT([r"$R_{DC_1}$", r"$R_{DC_2}$", "$dR_{x_1}$", "$dR_{x_2}$", "$dR_{y_1}$", "$dR_{y_2}$"], duration=0, ylabel="R ($\Omega$)", semilogy=True)
plt.show(block=False)
plt.pause(0.1)
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
        plot0.fig.savefig(fname=f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment_name} - thermalization - {val_t:.1f} K.png", format="png", dpi=300)
        print("Done.")

    elif settings.tc.address is None:

        input(f"Set temperature to {val_t:04.1f} K, wait for thermalization, then press Enter to continue...")

    # endregion

    # region ----- Set thermometer(s) current -----
    print(f"Setting thermometer(s) current from {0:.1f} uA to {1e6*i_th_ex:04.1f} uA... ", end="")
    temp = linspace(0, i_th_ex, i_th_ex_steps)
    adc.adw.Set_Par(41, len(temp))  # set length of arrays
    adc.adw.SetData_Long(list(adc.voltage2bin(temp / settings.src1.gain, bits=settings.adc.output_resolution)), 21, 1, len(temp))  # set ao1 data
    adc.adw.SetData_Long(list(adc.voltage2bin(temp / settings.src2.gain, bits=settings.adc.output_resolution)), 22, 1, len(temp))  # set ao1 data
    if thermometer == 0:
        process_n = 7
    elif thermometer == 1:
        process_n = 5
    elif thermometer == 2:
        process_n = 6
    adc.start_process(process_n)
    while adc.adw.Process_Status(process_n):
        plt.pause(0.1)
    print("Done.")  # endregion

    for idx_i_h, val_i_h in enumerate(i_h):

        # region ----- Set heater current -----
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

        if settings.lockin1.address is not None:
            print(f"Setting heater current from {1e3 * val_i_h_:.1f} mA to {1e3 * val_i_h:.1f} mA... ", end="")
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
        if thermometer == 0 or thermometer == 1:
            rho1 = zeros(len(f))
            phi1 = zeros(len(f))

        if thermometer == 0 or thermometer == 2:
            rho2 = zeros(len(f))
            phi2 = zeros(len(f))

        for idx_f, val_f in enumerate(f):

            # region ----- Set settling and measurement time -----
            print("Setting settling time and measurement time... ", end="")
            if val_f < 10:
                if thermometer == 1 or thermometer == 3:
                    lockin1.set_integration_time(3)
                if thermometer == 2 or thermometer == 3:
                    lockin2.set_integration_time(3)
                settling_time = 3 * 10 * 3
                measurement_time = 3 * 10
            elif (val_f >= 10) and (val_f < 100):
                if thermometer == 1 or thermometer == 3:
                    lockin1.set_integration_time(1)
                if thermometer == 2 or thermometer == 3:
                    lockin2.set_integration_time(1)
                settling_time = 1 * 10 * 3
                measurement_time = 1 * 10
            elif val_f >= 100:
                if thermometer == 1 or thermometer == 3:
                    lockin1.set_integration_time(100e-3)
                if thermometer == 2 or thermometer == 3:
                    lockin2.set_integration_time(100e-3)
                settling_time = 1 * 10 * 3
                measurement_time = 0.1 * 10
            print("Done.")  # endregion

            # region ----- Set Lockin frequency -----
            print(f"Setting lockin frequency to {val_f:.1f} Hz... ", end="")
            lockin1.set_frequency(val_f)
            print("Done")  # endregion

            # region ----- Measure oscillations (and plot in real time) -----
            print("Measuring oscillations... ", end="")
            vt_samples = int(ceil((settling_time + measurement_time) / (settings.adc.n_plc / settings.adc.line_freq)))
            plot2.ax.set_xlim([0, settling_time + measurement_time])
            adc.adw.Set_Par(41, vt_samples)

            adc_time = idx2time(linspace(0, vt_samples, vt_samples, endpoint=False), settings.adc.n_plc, settings.adc.line_freq)
            if thermometer == 0 or thermometer == 1:
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].time = adc_time
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].raw = zeros(vt_samples)
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].x = zeros(vt_samples)
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].y = zeros(vt_samples)
            if thermometer == 0 or thermometer == 2:
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].time = adc_time
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].raw = zeros(vt_samples)
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].x = zeros(vt_samples)
                data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].y = zeros(vt_samples)

            idx_ = 0
            adc.adw.Start_Process(4)
            while adc.process_status(4) is True:

                if adc.adw.Process_Status(4):
                    idx = adc.adw.Get_Par(35) - 1  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)
                else:
                    idx = adc.adw.Get_Par(35)  # param 35 is the scan index (the number of acquisitions completed is idx_scan - 1)

                if idx > idx_:
                    adc_time = idx2time(linspace(idx_, idx, idx - idx_, endpoint=False), settings.adc.n_plc, settings.adc.line_freq)

                    if thermometer == 0 or thermometer == 1:
                        # read from adc
                        ai1 = ctypeslib.as_array(adc.adw.GetData_Float(1, idx_ + 1, idx - idx_))
                        ai3 = ctypeslib.as_array(adc.adw.GetData_Float(3, idx_ + 1, idx - idx_))
                        ai5 = ctypeslib.as_array(adc.adw.GetData_Float(5, idx_ + 1, idx - idx_))
                        # convert data
                        v1 = adc.bin2voltage(ai1, bits=settings.adc.input_resolution) / settings.avv1.gain / i_th_ex  # raw
                        v3 = adc.bin2voltage(ai3, bits=settings.adc.input_resolution) * settings.lockin1.sensitivity / 10 / settings.avv1.gain / i_th_ex  # x
                        v5 = - adc.bin2voltage(ai5, bits=settings.adc.input_resolution) * settings.lockin1.sensitivity / 10 / settings.avv1.gain / i_th_ex  # y

                        # store converted data in data object
                        data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].raw[idx_:idx] = v1
                        data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].x[idx_:idx] = v3
                        data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].y[idx_:idx] = v5

                        # update plot
                        plot2.ax.lines[0].set_data(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].time[0:idx], abs(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].raw[0:idx]))
                        plot2.ax.lines[2].set_data(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].time[0:idx], abs(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].x[0:idx]))
                        plot2.ax.lines[4].set_data(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].time[0:idx], abs(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt1"].y[0:idx]))

                    if thermometer == 0 or thermometer == 2:
                        ai2 = ctypeslib.as_array(adc.adw.GetData_Float(2, idx_ + 1, idx - idx_))
                        ai4 = ctypeslib.as_array(adc.adw.GetData_Float(4, idx_ + 1, idx - idx_))
                        ai6 = ctypeslib.as_array(adc.adw.GetData_Float(6, idx_ + 1, idx - idx_))
                        # convert data
                        v2 = adc.bin2voltage(ai2, bits=settings.adc.input_resolution) / settings.avv2.gain / i_th_ex  # raw
                        v4 = adc.bin2voltage(ai4, bits=settings.adc.input_resolution) * settings.lockin2.sensitivity / 10 / settings.avv2.gain / i_th_ex  # x
                        v6 = - adc.bin2voltage(ai6, bits=settings.adc.input_resolution) * settings.lockin2.sensitivity / 10 / settings.avv2.gain / i_th_ex  # y

                        # store converted data in data object
                        data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].raw[idx_:idx] = v2
                        data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].x[idx_:idx] = v4
                        data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].y[idx_:idx] = v6

                        # update plot
                        plot2.ax.lines[1].set_data(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].time[0:idx], abs(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].raw[0:idx]))
                        plot2.ax.lines[3].set_data(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].time[0:idx], abs(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].x[0:idx]))
                        plot2.ax.lines[5].set_data(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].time[0:idx], abs(data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][idx_f]["drt2"].y[0:idx]))

                    idx_ = idx
                plot2.ax.relim()
                plot2.ax.autoscale_view(scalex=False, scaley=True)
                plt.pause(0.5)
            print("Done.")

            print("Saving oscillations figure to disc... ", end="")
            plot2.fig.savefig(fname=f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment_name} - oscillations - {val_t:.1f} K - {val_i_h * 1000:.1f} mA - {val_f:.1f} Hz.png", format="png", dpi=300)
            print("Done.")
            # endregion

            # region ----- Read and store data locally -----
            print("Reading data from ADC... ", end="")
            vt_samples2avg = int(ceil(measurement_time / (settings.adc.n_plc / settings.adc.line_freq)))

            if thermometer == 0 or thermometer == 1:
                # read from adc
                ai1 = ctypeslib.as_array(adc.adw.GetData_Float(1, 1, vt_samples))
                ai3 = ctypeslib.as_array(adc.adw.GetData_Float(3, 1, vt_samples))
                ai5 = ctypeslib.as_array(adc.adw.GetData_Float(5, 1, vt_samples))
                # convert data
                v1 = adc.bin2voltage(ai1, bits=settings.adc.input_resolution) / settings.avv1.gain / i_th_ex  # raw
                v3 = adc.bin2voltage(ai3, bits=settings.adc.input_resolution) * settings.lockin1.sensitivity / 10 / settings.avv1.gain / i_th_ex  # x
                v5 = - adc.bin2voltage(ai5, bits=settings.adc.input_resolution) * settings.lockin1.sensitivity / 10 / settings.avv1.gain / i_th_ex  # y
                rho1[idx_f] = mean(sqrt(v3[-vt_samples2avg:] ** 2 + v5[-vt_samples2avg:] ** 2))
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

            if thermometer == 0 or thermometer == 2:
                ai2 = ctypeslib.as_array(adc.adw.GetData_Float(2, 1, vt_samples))
                ai4 = ctypeslib.as_array(adc.adw.GetData_Float(4, 1, vt_samples))
                ai6 = ctypeslib.as_array(adc.adw.GetData_Float(6, 1, vt_samples))
                # convert data
                v2 = adc.bin2voltage(ai2, bits=settings.adc.input_resolution) / settings.avv2.gain / i_th_ex  # raw
                v4 = adc.bin2voltage(ai4, bits=settings.adc.input_resolution) * settings.lockin2.sensitivity / 10 / settings.avv2.gain / i_th_ex  # x
                v6 = - adc.bin2voltage(ai6, bits=settings.adc.input_resolution) * settings.lockin2.sensitivity / 10 / settings.avv2.gain / i_th_ex  # y
                rho2[idx_f] = mean(sqrt(v4[-vt_samples2avg:] ** 2 + v6[-vt_samples2avg:] ** 2))
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

            if thermometer == 0 or thermometer == 1:

                plot1.axx.lines[2 * idx_i_h].set_data(f[0:idx_f+1], [data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][k]["drt1"].x_avg for k in range(idx_f+1)])
                plot1.axy.lines[2 * idx_i_h].set_data(f[0:idx_f+1], [data.t[idx_t]["dr"][f"h{heater}"][idx_i_h][k]["drt1"].y_avg for k in range(idx_f+1)])

                plot1.axr.lines[2 * idx_i_h].set_data(f[0:idx_f+1], rho1[0:idx_f+1])
                plot1.axp.lines[2 * idx_i_h].set_data(f[0:idx_f+1], phi1[0:idx_f+1])

            if thermometer == 0 or thermometer == 2:

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
            plt.pause(0.5)
            print("Done.")  # endregion

            print("Saving oscillations figure to disc... ", end="")
            plot1.fig.savefig(fname=f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment_name}.png", format="png", dpi=300)
            print("Done.")

    # region ----- Set thermometer(s) current -----
    print(f"Setting thermometer(s) current from {1e6*i_th_ex:04.1f} uA to {0:04.1f} uA... ", end="")
    temp = linspace(i_th_ex, 0, i_th_ex_steps)
    adc.adw.Set_Par(41, len(temp))  # set length of arrays
    adc.adw.SetData_Long(list(adc.voltage2bin(temp / settings.src1.gain, bits=settings.adc.output_resolution)), 21, 1, len(temp))  # set ao1 data
    adc.adw.SetData_Long(list(adc.voltage2bin(temp / settings.src2.gain, bits=settings.adc.output_resolution)), 22, 1, len(temp))  # set ao1 data
    if thermometer == 0:
        process_n = 7
    elif thermometer == 1:
        process_n = 5
    elif thermometer == 2:
        process_n = 6
    adc.start_process(process_n)
    while adc.adw.Process_Status(process_n):
        plt.pause(0.1)
    print("Done.")  # endregion

    # region ----- Ramp down heater current -----
    if settings.lockin1.address is not None:
        print(f"Setting heater current from {1e3 * val_i_h:.1f} mA to {0:.1f} mA... ", end="")
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
        if os.path.exists(experiment.backup_filename):
            os.remove(experiment.backup_filename)
        os.rename(experiment.filename, experiment.backup_filename)
    with open(experiment.filename, "wb") as file:
        pickle.dump(experiment, file)
    print("Done.")
    print("Saving figure to disc... ", end="")
    plot1.fig.savefig(fname=f"{experiment.date.strftime('%Y-%m-%d %H.%M.%S')} - {experiment.chip} - {experiment.device} - {experiment.experiment_name} - {val_t:04.1f} K - {1e3 * val_i_h:04.1f} mA - {f[0]:.1f} Hz - {f[-1]:04.1f} Hz.png", format="png", dpi=300)
    print("Done.")
    # endregion

plt.show(block=False)
input("measurement complete. Ground the device then press Enter to terminate.")
exit()
