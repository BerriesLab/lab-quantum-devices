# region ----- Import packages -----
import keithley_smu236
import keithley_dmm2182a
import srs_sr830
import srs_srcs580
import lakeshore_tc336
import oxford_mercury_itc
import pyvisa
import scipy.stats
import os
import numpy as np
from numpy import mean, std, trim_zeros
import pickle
from Objects.Backup.measurement_objects import *
from Objects.Backup.plot_objects import *
import time
# endregion

#######################################################################
#   Author:         Davide Beretta
#   Date:           06.05.2021
#   Description:    TE-FET: calibration
#######################################################################

# region ----- measurement(s) options -----
box = experiment()
box.main = r"E:\Samples"
box.date = datetime.datetime.now()
box.filename = "{} - calibration".format(box.date.strftime("%Y.%m.%d %H.%M.%S"))
box.backupname = box.filename + ".bak"
box.experiment = "calibration"
box.chip = "test"
box.device = "20"
# ---------------------------------------
t = linspace(290, 292, 3)                       # [1D array] temperatures (in K) where calibration occurs.
i_h = linspace(0e-3, 3e-3, 4)                   # [1D array] heater current (in A) where heater calibration occurs. Start, stop, step.
t_h = array([290, 292])                              # [1D array] temperatures (in K) where heater calibration occurs. Pass an empty array
i_th = linspace(0, 50e-6, 11)                   # [1D array] thermometer current for iv (in A).
box.data = calibration(t, t_h, i_h, i_th)
box.data.thermometer = "both"                   # [string or int] select the thermometer to calibrate: "1" (int), "2" (int), or "both" (string)
box.data.i_th_ex = 50e-6                        # [float] thermometer excitation current
box.data.heater = 1                             # [int] select heater in use (it has no practical effect on the code)
box.data.t_settling_time = 1 * 60              # [float] cryostat thermalization time (in s).
box.data.t_settling_time_init = 1 * 60         # [float] cryostat initial thermalization time (in s).
box.data.t_dt_lift = np.inf                     # [float] temperature interval in between needles lifting (in K). Note: set to inf for Heliox
box.data.i_settling_time = 2 * 60               # [float] heater thermalization time (in s)
box.data.iv_check = False                       # [boolean]: True to activate user input after iv
# endregion

# region ----- Settings ------
# ----- tc settings -----
box.settings.__setattr__("tc", settings())
box.settings.tc.address = "ASRL4::INSTR"        # [string] address of temperature controller
box.settings.tc.model = 1                       # [string] select tc_model (0: lakeshore 336, 1: oxford mercury itc)
box.settings.tc.t_switch = 50                   # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium"
box.settings.tc.sampling_freq_plot = 2          # [int] temperature sampling frequency (in Hz)
# ----- smu1 settings -----
box.settings.__setattr__("smu1", settings())
box.settings.smu1.address = "GPIB0::1"          # [string] address of smu 1
box.settings.smu1.source_range = 100e-6         # [float] current source range
box.settings.smu1.compliance = 1                # [float] voltage compliance
box.settings.smu1.delay = 0.1                   # [float] time interval (in s) between source and measure (software controlled)
# ----- smu2 settings -----
box.settings.__setattr__("smu2", settings())
box.settings.smu2.address = "GPIB0::2"          # [string] address of smu 2
box.settings.smu2.source_range = box.settings.smu1.source_range
box.settings.smu2.compliance = box.settings.smu1.compliance
box.settings.smu2.delay = box.settings.smu1.delay
# ----- dmm1 settings -----
box.settings.__setattr__("dmm1", settings())
box.settings.dmm1.address = "GPIB0::3"          # [string] address of dmm 1
box.settings.dmm1.nplc = 1                      # [float] nplc of dmm
box.settings.dmm1.sense_range = 10e-3           # [float] range of dmm
box.settings.dmm1.digital_samples = 1           # [int] digital samples averaged by dmm (1 - 9999)
box.settings.dmm1.lpf = "on"                    # [string] status of low pass filter (cutoff frequency at 18 Hz)
# ----- dmm2 settings -----
box.settings.__setattr__("dmm2", settings())
box.settings.dmm2.address = "GPIB0::4"          # [string] address of dmm 2
box.settings.dmm2.nplc = box.settings.dmm1.nplc
box.settings.dmm2.sense_range = box.settings.dmm1.sense_range
box.settings.dmm2.digital_samples = box.settings.dmm1.digital_samples
box.settings.dmm2.lpf = box.settings.dmm1.lpf
# ----- lock-in1 settings -----
box.settings.__setattr__("lockin1", settings())
box.settings.lockin1.address = "GPIB0::6"       # [string] address of lockin 1
box.settings.lockin1.reference = "internal"
box.settings.lockin1.freq = 7.745               # [float] excitation current frequency (in Hz)
box.settings.lockin1.sampling_freq_plot = 2     # [float] sampling frequency
box.settings.lockin1.sampling_freq = 512        # [float] sampling frequency
box.settings.lockin1.samples = 512 * 10         # [int] number of samples recorded (and averaged in the script) by lockin in buffer (max 16383)
box.settings.lockin1.shield = "float"           # [string] shield ca nbe floating or shorted
box.settings.lockin1.coupling = "ac"            # [string] coupling can be ac or dc
box.settings.lockin1.time = 3                   # [float] integration time
box.settings.lockin1.filter = "24 dB/oct"       # [string] filter
box.settings.lockin1.input = "a-b"              # [string] input can be single ended or differential
box.settings.lockin1.sensitivity = "20 uV/pA"   # [string] sensitivity. The "/" is not a division symbols but stands for either Volts or Amperes.
box.settings.lockin1.harmonic = 2               # [int] demodulated harmonic
box.settings.lockin1.reserve = "normal"         # [string] reserve
# ----- lock-in2 settings -----
box.settings.__setattr__("lockin2", settings())
box.settings.lockin2.address = "GPIB0::11"      # [string] address of lockin 2
box.settings.lockin2.reference = "external"
box.settings.lockin2.freq = 7.745               # [float] excitation current frequency (in Hz)
box.settings.lockin2.sampling_freq_plot = 2     # [float] sampling frequency
box.settings.lockin2.sampling_freq = 512        # [float] sampling frequency
box.settings.lockin2.samples = 512 * 10         # [int] number of samples recorded (and averaged in the script) by lockin in buffer (max 16383)
box.settings.lockin2.shield = "float"           # [string] shield ca nbe floating or shorted
box.settings.lockin2.coupling = "ac"            # [string] coupling can be ac or dc
box.settings.lockin2.time = 3                   # [float] integration time
box.settings.lockin2.filter = "24 dB/oct"       # [string] filter
box.settings.lockin2.input = "a-b"              # [string] input can be single ended or differential
box.settings.lockin2.sensitivity = "20 uV/pA"   # [string] sensitivity. The "/" is not a division symbols but stands for either Volts or Amperes.
box.settings.lockin2.harmonic = 2               # [int] demodulated harmonic
box.settings.lockin2.reserve = "normal"         # [string] reserve
# ----- aiv settings -----
box.settings.__setattr__("aiv", settings())
box.settings.aiv.address = "ASRL2::INSTR"       # [string] address of aiv
box.settings.aiv.gain = 10e-3                   # [float] set the gain of the voltage controlled current amplifier
box.settings.aiv.isolation = "float"            # [string] isolation
box.settings.aiv.shield = "return"              # [string] shield
box.settings.aiv.compliance = 50                # [float] set the compliance to the highest level
box.settings.aiv.response = "fast"              # [string] set the response
# endregion

# region ----- Read resources and create instrumentation objects -----
print("\n***** Loading instrumentation drivers *****")
# Create a Resource Manager
rm = pyvisa.ResourceManager()
try:
    # define smu1 object for thermometer 1
    smu1 = keithley_smu236.smu236(visa=rm.open_resource(box.settings.smu1.address))
    print("Found smu 1: {}".format(smu1.read_model()))
except pyvisa.VisaIOError as e:
    raise pyvisa.VisaIOError("Cannot find smu 1... Execution terminated.")
try:
    # define smu2 object for thermometer 2
    smu2 = keithley_smu236.smu236(visa=rm.open_resource(box.settings.smu2.address))
    print("Found smu 2: {}".format(smu2.read_model()))
except pyvisa.VisaIOError as e:
    raise pyvisa.VisaIOError("Cannot find smu 2... Execution terminated.")
try:
    # define dmm 1 object for thermometer 1
    dmm1 = keithley_dmm2182a.dmm2182a(visa=rm.open_resource(box.settings.dmm1.address))
    print("Found dmm 1: {}".format(dmm1.read_model()))
    dmm1.visa.timeout = None
except pyvisa.VisaIOError as e:
    raise pyvisa.VisaIOError("Cannot dmm 1... Execution terminated.")
try:
    # define dmm 2 object for thermometer 1
    dmm2 = keithley_dmm2182a.dmm2182a(visa=rm.open_resource(box.settings.dmm2.address))
    print("Found dmm 2: {}".format(dmm2.read_model()))
    dmm2.visa.timeout = None
except pyvisa.VisaIOError as e:
    raise pyvisa.VisaIOError("Cannot find dmm 2... Execution terminated.")
try:
    # define lock-in 1 object for thermometer 1 (voltage measurement)
    lockin1 = srs_sr830.sr830(visa=rm.open_resource(box.settings.lockin1.address))
    print("Found lock-in 1: {}".format(lockin1.read_model()))
    lockin1.visa.timeout = None
except pyvisa.VisaIOError as e:
    raise pyvisa.VisaIOError("Cannot find lock-in 1... Execution terminated.")
try:
    # define lock-in 2 object for thermometer 1 (voltage measurement)
    lockin2 = srs_sr830.sr830(visa=rm.open_resource(box.settings.lockin2.address))
    print("Found lock-in 2: {}".format(lockin2.read_model()))
    lockin2.visa.timeout = None
except pyvisa.VisaIOError as e:
    raise pyvisa.VisaIOError("Cannot find lock-in 2... Execution terminated.")
try:
    # define I/V current amplifier object for heater current
    aiv = srs_srcs580.srcs580(visa=rm.open_resource(box.settings.aiv.address))
    print("Found I/V current amplifier: {}".format(aiv.read_model()))
except pyvisa.VisaIOError as e:
    raise pyvisa.VisaIOError("Cannot find I/V current amplifier... Execution terminated.")
if box.settings.tc.model == 0:
    try:
        # define temperature controller visa object for Lakeshore 336
        tc = lakeshore_tc336.tc336(visa=rm.open_resource(box.settings.tc.address))
        print("Found temperature controller: {}".format(tc.read_model()))
    except pyvisa.VisaIOError as e:
        raise pyvisa.VisaIOError("Cannot find temperature controller... Execution terminated.")
elif box.settings.tc.model == 1:
    try:
        # define temperature controller visa object for Oxford Mercury ITC
        tc = oxford_mercury_itc.mercuryitc(visa=rm.open_resource(box.settings.tc.address))
        print("Found temperature controller: {}".format(tc.read_model()))
    except pyvisa.VisaIOError as e:
        raise pyvisa.VisaIOError("Cannot find temperature controller... Execution terminated.")
else:
    raise ValueError("Temperature controller ID does not belong to the list of the accepted values.")
# endregion

# region ----- Estimate measurement time -----
estimated_time_to_lift = (box.data.t_dt_lift / (box.data.t[1]-box.data.t[0])) * box.data.t_settling_time
estimated_measurement_time = box.data.t_settling_time_init + len(box.data.t) * box.data.t_settling_time + len(box.data.i_h) * box.data.i_settling_time
# endregion

# region ----- Message to the user -----
print("Checking USER entries... ", end="")
if box.data.thermometer not in [1, 2, "both"]:
    raise ValueError("\nThermometer ID does not belong to the list of the accepted values.")
if box.data.heater not in [1, 2]:
    raise ValueError("\nHeater ID does not belong to the list of the accepted values.")
print("Done.")
print("\n"
      "***** Measurement summary *****\n"
      "chip: {}\n"
      "device: {}\n"
      "thermometer(s): {}\n"
      "heater: {}\n"
      "temperatures: {} K\n"
      "heater calibration at: {} K\n"
      "heater current: {} mA".format(box.chip, box.device, box.data.thermometer, box.data.heater, box.data.t, box.data.t_h, 1000 * box.data.i_h,))
if box.data.iv_check is True:
    print("The USER will be asked to accept each measured iv before proceeding.")
if abs(box.data.t.max() - box.data.t.min()) > box.data.t_dt_lift:
    print("The USER will be asked to raise and lower back the probes during the measurement to relax mechanical tension.\n"
          "Estimated measurement time before USER action is required: {:04.1f} min.".format(estimated_time_to_lift/3600))
    print("Estimated measurement time: {:04.1f} min.".format(estimated_measurement_time/3600))
else:
    print("No action is required from the USER during the measurement.\n"
          "Estimated measurement time: " + "{:04.1f} h.".format(estimated_measurement_time/3600))
input("Gate must be grounded before proceeding.\n"
      "Press Enter to accept and proceed, press Ctrl-C to abort.")
# endregion

# region ----- Set or create current directory where to save files -----
print("\n***** Measurement log *****")
path = box.main + "\\" + box.chip + "\\" + box.device + "\\"
try:
    os.chdir(path)  # if path exists, then make it cwd
    print("{} ... found.".format(path))
except OSError:  # if path does not exists
    print("{} ... not found. Making directory... ".format(path))
    os.makedirs(path)  # make new directory
    os.chdir(path)  # make path cwd
print("Current working directory set to: {}".format(os.getcwd()))
# endregion

# region ----- Configure instrumentation -----
print("Configuring instrumentation... ", end="")
lockin1.configure(box.settings.lockin1.reference, 0, box.settings.lockin1.freq, box.settings.lockin1.harmonic,
                  box.settings.lockin1.input, box.settings.lockin1.shield, box.settings.lockin1.coupling,
                  box.settings.lockin1.sensitivity, box.settings.lockin1.reserve, box.settings.lockin1.time,
                  box.settings.lockin1.filter, "both", box.settings.lockin1.sampling_freq, "shot", "off")
lockin2.configure(box.settings.lockin2.reference, 0, box.settings.lockin2.freq, box.settings.lockin2.harmonic,
                  box.settings.lockin2.input, box.settings.lockin2.shield, box.settings.lockin2.coupling,
                  box.settings.lockin2.sensitivity, box.settings.lockin2.reserve, box.settings.lockin2.time,
                  box.settings.lockin2.filter, "both", box.settings.lockin2.sampling_freq, "shot", "off")
aiv.configure(box.settings.aiv.gain, box.settings.aiv.response, box.settings.aiv.shield, box.settings.aiv.isolation,
              "on", "on", box.settings.aiv.compliance)
smu1.bias("i", 0, box.settings.smu1.source_range, "auto", 0, 0, 20e-3, "local", box.settings.smu1.compliance)  # bias 0 A on a 100 uA range
dmm1.configure(box.settings.dmm1.lpf, box.settings.dmm1.digital_samples, box.settings.dmm1.sense_range,
               box.settings.dmm1.nplc, "bus", "inf", "default", "on", "off")  # load reading program in dmm 1
smu2.bias("i", 0, box.settings.smu2.source_range, "auto", 0, 0, 20e-3, "local", box.settings.smu2.compliance)  # bias 0 A on a 100 uA range
dmm2.configure(box.settings.dmm2.lpf, box.settings.dmm2.digital_samples, box.settings.dmm2.sense_range,
               box.settings.dmm2.nplc, "bus", "inf", "default", "on", "off")  # load reading program in dmm 2
print("Done.")
# endregion

# region ----- Initialize figures -----
print("Initializing figure... ", end="")
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
plot1 = plot_calibration(box.data)
plot2 = plot_tt(box.data)
plot3 = plot_drt(box.data)
plt.show(block=False)
plt.pause(.1)
print("Done.")
# endregion

input("Unground the device, then press Enter to start measurement...")
# set the temperature at which needles must be lifted and then lowered again before continuing
t_lift = box.data.t.min() + box.data.t_dt_lift

for idx_t, val_t in enumerate(box.data.t):

    # region ----- Lift needles if needed -----
    if val_t > t_lift:  # check if user must lift needles
        input("Please ground the device, lift and then lower the probes back into position. "
              "Then unground the device and press Enter to continue...")
        t_lift = val_t + box.data.t_dt_lift  # update temperature lift value
    # endregion

    # region ----- Set temperature and wait for thermalization -----
    tc.set_temperature(output=0, setpoint=val_t)
    tc.set_temperature(output=1, setpoint=val_t) if box.settings.tc.model == 0 else None

    print("Waiting for thermalization at {:04.1f} K...".format(val_t), end="")
    settling_time = box.data.t_settling_time_init if idx_t == 0 else box.data.t_settling_time
    box.data.tt[idx_t].setpoint = val_t
    box.data.tt[idx_t].time = zeros(int(ceil(settling_time * box.settings.tc.sampling_freq_plot)))
    box.data.tt[idx_t].temperature_stage = zeros(int(ceil(settling_time * box.settings.tc.sampling_freq_plot)))
    box.data.tt[idx_t].temperature_shield = zeros(int(ceil(settling_time * box.settings.tc.sampling_freq_plot)))

    k = 0
    t0 = time.time()
    while time.time() - t0 <= settling_time:
        box.data.tt[idx_t].time[k] = time.time() - t0
        box.data.tt[idx_t].temperature_stage[k] = tc.read_temperature("a")
        box.data.tt[idx_t].temperature_shield[k] = tc.read_temperature("b")
        plot2.at.axhline(y=val_t, linestyle="--")
        plot2.show_setpoint(val_t)
        plot2.ln1 = plot2.update(plot2.at, plot2.ln1, x=box.data.tt[idx_t].time[0:k + 1], y=box.data.tt[idx_t].temperature_stage[0:k + 1], linewidth=0, marker="o", markeredgecolor="black", markerfacecolor="orange", alpha=0.4)
        if box.settings.tc.model == 0:
            plot2.ln2 = plot2.update(plot2.at, plot2.ln2, x=box.data.tt[idx_t].time[0:k+1], y=box.data.tt[idx_t].temperature_shield[0:k+1], linewidth=0, marker="o", markeredgecolor="black", markerfacecolor="green", alpha=0.4)
        plt.pause(1 / box.settings.tc.sampling_freq_plot)
        k = k + 1
    print("Done.")

    # remove trailing zeros from arrays
    box.data.tt[idx_t].time = trim_zeros(box.data.tt[idx_t].time)
    box.data.tt[idx_t].temperature_stage = trim_zeros(box.data.tt[idx_t].temperature_stage)
    box.data.tt[idx_t].temperature_shield = trim_zeros(box.data.tt[idx_t].temperature_shield)

    # endregion

    accept = False  # initialize controlling variable to accept/reject the iv
    while accept is False:

        # region ----- Allocate RAM -----
        if box.data.thermometer == 1 or box.data.thermometer == "both":
            box.data.iv1[idx_t].temperature = val_t
            box.data.iv1[idx_t].i = box.data.i_th
            box.data.iv1[idx_t].v = zeros(len(box.data.i_th))
        if box.data.thermometer == 2 or box.data.thermometer == "both":
            box.data.iv2[idx_t].temperature = val_t
            box.data.iv2[idx_t].i = box.data.i_th
            box.data.iv2[idx_t].v = zeros(len(box.data.i_th))
        # endregion

        # region ----- Make iv -----
        print("Making iv(s)... ", end="")

        # measure
        for idx_i_th, val_i_th in enumerate(box.data.i_th):

            if box.data.thermometer == 1 or box.data.thermometer == "both":
                smu1.set_bias_level(bias=val_i_th, delay=box.settings.smu1.delay)
                dmm1.send_trigger()

            if box.data.thermometer == 2 or box.data.thermometer == "both":
                smu2.set_bias_level(bias=val_i_th, delay=box.settings.smu2.delay)
                dmm2.send_trigger()

            if box.data.thermometer == 1 or box.data.thermometer == "both":
                dmm1.wait_for_srq()
                box.data.iv1[idx_t].v[idx_i_th] = dmm1.read_last()
                dmm1.clear_measurement_event_register()
                plot1.lniv1[idx_t] = plot1.update(ax=plot1.iv1, ln=plot1.lniv1[idx_t], x=box.data.iv1[idx_t].i[0:idx_i_th+1], y=box.data.iv1[idx_t].v[0:idx_i_th+1], linewidth=0, marker="o", markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5, label="$Th_1$")

            if box.data.thermometer == 2 or box.data.thermometer == "both":
                dmm2.wait_for_srq()
                box.data.iv2[idx_t].v[idx_i_th] = dmm2.read_last()
                dmm2.clear_measurement_event_register()
                plot1.lniv2[idx_t] = plot1.update(ax=plot1.iv2, ln=plot1.lniv2[idx_t], x=box.data.iv2[idx_t].i[0:idx_i_th+1], y=box.data.iv2[idx_t].v[0:idx_i_th+1], linewidth=0, marker="D", markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5, label="$Th_2$")

        # set bias level to 0
        if box.data.thermometer == 1 or box.data.thermometer == "both":
            smu1.set_bias_level(0)
        if box.data.thermometer == 2 or box.data.thermometer == "both":
            smu2.set_bias_level(0)

        # calculate resistance of thermometer 1 and thermometer 2 and update plots
        if box.data.thermometer == 1 or box.data.thermometer == "both":
            fit1 = scipy.stats.linregress(box.data.iv1[idx_t].i, box.data.iv1[idx_t].v)
            box.data.iv1[idx_t].r = fit1[0]
            box.data.iv1[idx_t].r_stderr = fit1[4]
            plot1.lnr1t = plot1.update(ax=plot1.rt, ln=plot1.lnr1t, x=box.data.t[0: idx_t+1], y=array([box.data.iv1[k].r for k in range(idx_t+1)]), linewidth=0, marker="o", markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5, label="$Th_1$")
            plot1.lnr1terr = plot1.update(ax=plot1.rterr, ln=plot1.lnr1terr, x=box.data.t[0: idx_t+1], y=array([box.data.iv1[k].r_stderr for k in range(idx_t+1)]), linewidth=0, marker="o", markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5, label="$Th_1$")

        if box.data.thermometer == 2 or box.data.thermometer == "both":
            fit2 = scipy.stats.linregress(box.data.iv2[idx_t].i, box.data.iv2[idx_t].v)
            box.data.iv2[idx_t].r = fit2[0]
            box.data.iv2[idx_t].r_stderr = fit2[4]
            plot1.lnr2t = plot1.update(ax=plot1.rt, ln=plot1.lnr2t, x=box.data.t[0: idx_t+1], y=array([box.data.iv2[k].r for k in range(idx_t+1)]), linewidth=0, marker="D", markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5, label="$Th_2$")
            plot1.lnr2terr = plot1.update(ax=plot1.rterr, ln=plot1.lnr2terr, x=box.data.t[0: idx_t+1], y=array([box.data.iv2[k].r_stderr for k in range(idx_t+1)]), linewidth=0, marker="D", markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5, label="$Th_2$")
        # endregion

        # region ----- Prompt user -----
        if box.data.iv_check is False:
            accept = True
            print("Done.")
        elif box.data.iv_check is True:
            accept = None
            while (accept is not True) and (accept is not False):
                accept = input("Accept iv and continue measurement? (y/n)")
                if accept == "y":
                    accept = True
                    print("iv accepted. Measurement continues.")
                elif accept == "n":
                    accept = False
                    input("iv rejected. Make the proper adjustments and then press Enter to repeat iv.")
                else:
                    accept = None
                    print("Invalid input. Input must be either 'y' (to accept) or 'n' (to reject).")
        # endregion

    idx_t_h = 0
    if val_t in box.data.t_h:

        accept = False  # initialize controlling variable to accept/reject the calibration
        while accept is False:

            print("Starting heater calibration at {} K...".format(t))

            for idx_i_h, val_i_h in enumerate(box.data.i_h):

                # region ----- Allocate RAM ----------------------------------------------
                print("Allocating RAM... ", end="")
                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    box.data.dr1t[idx_t_h][idx_i_h].temperature = val_t
                    box.data.dr1t[idx_t_h][idx_i_h].i_h = val_i_h
                    box.data.dr1t[idx_t_h][idx_i_h].time = zeros(int(ceil(box.data.i_settling_time * box.settings.lockin1.sampling_freq_plot)))
                    box.data.dr1t[idx_t_h][idx_i_h].drx = zeros(int(ceil(box.data.i_settling_time * box.settings.lockin1.sampling_freq_plot)))
                    box.data.dr1t[idx_t_h][idx_i_h].dry = zeros(int(ceil(box.data.i_settling_time * box.settings.lockin1.sampling_freq_plot)))
                    box.data.dr1t[idx_t_h][idx_i_h].drx_raw = zeros(box.settings.lockin1.samples)
                    box.data.dr1t[idx_t_h][idx_i_h].dry_raw = zeros(box.settings.lockin1.samples)
                    box.data.dr1lpft[idx_t_h][idx_i_h].i = box.data.i_th
                    box.data.dr1lpft[idx_t_h][idx_i_h].v = zeros(len(box.data.i_th))

                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    box.data.dr2t[idx_t_h][idx_i_h].temperature = val_t
                    box.data.dr2t[idx_t_h][idx_i_h].i_h = val_i_h
                    box.data.dr2t[idx_t_h][idx_i_h].temperature = val_t
                    box.data.dr2t[idx_t_h][idx_i_h].time = zeros(int(ceil(box.data.i_settling_time * box.settings.lockin1.sampling_freq_plot)))
                    box.data.dr2t[idx_t_h][idx_i_h].drx = zeros(int(ceil(box.data.i_settling_time * box.settings.lockin1.sampling_freq_plot)))
                    box.data.dr2t[idx_t_h][idx_i_h].dry = zeros(int(ceil(box.data.i_settling_time * box.settings.lockin1.sampling_freq_plot)))
                    box.data.dr2t[idx_t_h][idx_i_h].drx_raw = zeros(box.settings.lockin2.samples)
                    box.data.dr2t[idx_t_h][idx_i_h].dry_raw = zeros(box.settings.lockin2.samples)
                    box.data.dr2lpft[idx_t_h][idx_i_h].i = box.data.i_th
                    box.data.dr2lpft[idx_t_h][idx_i_h].v = zeros(len(box.data.i_th))

                print("Done.")  # endregion

                # region ----- Ramp up thermometers current ------------------------------
                print("Ramping up thermometer(s) current to {} A... ".format(box.data.i_th_ex), end="")
                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    smu1.sweep_bias("i", 0, box.data.i_th_ex, 100, 10e-6, box.settings.smu1.source_range, "auto", box.settings.smu1.compliance, 0, 20e-3, "local")
                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    smu2.sweep_bias("i", 0, box.data.i_th_ex, 100, 10e-6, box.settings.smu2.source_range, "auto", box.settings.smu2.compliance, 0, 20e-3, "local")
                print("Done.")  # endregion ----------------------------------------------

                # region ----- Ramp up heater current ------------------------------------
                print("Ramping up heater current at {} mA... ".format(val_i_h * 1000), end="")
                if val_i_h / box.settings.aiv.gain < 0.004:
                    aiv.operation(input="off", output="on")
                else:
                    aiv.operation(input="on", output="on")
                if idx_i_h == 0:
                    lockin1.sweep_v(start=0, stop=val_i_h / box.settings.aiv.gain / np.sqrt(2), n_step=1000, rate=10e-6 / box.settings.aiv.gain / np.sqrt(2))
                else:
                    lockin1.sweep_v(start=i_h[idx_i_h - 1] / box.settings.aiv.gain / np.sqrt(2), stop=val_i_h / box.settings.aiv.gain / np.sqrt(2), n_step=1000, rate=10e-6 / box.settings.aiv.gain / np.sqrt(2))
                print("Done.")  # endregion

                # region ----- Wait for steady state -------------------------------------
                t0 = time.time()
                print("Waiting for thermalization... ", end="")
                idx = 0
                while time.time() - t0 <= box.data.i_settling_time:

                    if box.data.thermometer == 1 or "both":
                        temp1, temp2 = lockin1.read()
                        box.data.dr1t[idx_t_h][idx_i_h].time[idx] = time.time() - t0
                        box.data.dr1t[idx_t_h][idx_i_h].drx[idx] = temp1 * np.sqrt(2) / box.data.i_th_ex
                        box.data.dr1t[idx_t_h][idx_i_h].dry[idx] = temp2 * np.sqrt(2) / box.data.i_th_ex
                        plot3.ln1x = plot3.update(ax=plot3.ax, ln=plot3.ln1x, x=box.data.dr1t[idx_t_h][idx_i_h].time[0:idx+1], y=box.data.dr1t[idx_t_h][idx_i_h].drx[0:idx+1], lw=0, marker="o", markerfacecolor="orange", markeredgecolor="black", alpha=0.5)
                        plot3.ln1y = plot3.update(ax=plot3.ax, ln=plot3.ln1y, x=box.data.dr1t[idx_t_h][idx_i_h].time[0:idx+1], y=box.data.dr1t[idx_t_h][idx_i_h].dry[0:idx+1], lw=0, marker="o", markerfacecolor="green", markeredgecolor="black", alpha=0.5)

                    if box.data.thermometer == 2 or "both":
                        temp1, temp2 = lockin2.read()
                        box.data.dr2t[idx_t_h][idx_i_h].time[idx] = time.time() - t0
                        box.data.dr2t[idx_t_h][idx_i_h].drx[idx] = temp1 * np.sqrt(2) / box.data.i_th_ex
                        box.data.dr2t[idx_t_h][idx_i_h].dry[idx] = temp2 * np.sqrt(2) / box.data.i_th_ex
                        plot3.ln2x = plot3.update(ax=plot3.ax, ln=plot3.ln2x, x=box.data.dr2t[idx_t_h][idx_i_h].time[0:idx+1], y=box.data.dr2t[idx_t_h][idx_i_h].drx[0:idx+1], lw=0, marker="D", markerfacecolor="orange", markeredgecolor="black", alpha=0.5)
                        plot3.ln2y = plot3.update(ax=plot3.ax, ln=plot3.ln2y, x=box.data.dr2t[idx_t_h][idx_i_h].time[0:idx+1], y=box.data.dr2t[idx_t_h][idx_i_h].dry[0:idx+1], lw=0, marker="D", markerfacecolor="green", markeredgecolor="black", alpha=0.5)

                    plt.pause(1 / box.settings.lockin1.sampling_freq_plot)
                    idx = idx + 1

                # remove trailing zeros from arrays
                box.data.dr1t[idx_t_h][idx_i_h].time = trim_zeros(box.data.dr1t[idx_t_h][idx_i_h].time)
                box.data.dr1t[idx_t_h][idx_i_h].drx = trim_zeros(box.data.dr1t[idx_t_h][idx_i_h].drx)
                box.data.dr1t[idx_t_h][idx_i_h].dry = trim_zeros(box.data.dr1t[idx_t_h][idx_i_h].dry)
                box.data.dr2t[idx_t_h][idx_i_h].time = trim_zeros(box.data.dr2t[idx_t_h][idx_i_h].time)
                box.data.dr2t[idx_t_h][idx_i_h].drx = trim_zeros(box.data.dr2t[idx_t_h][idx_i_h].drx)
                box.data.dr2t[idx_t_h][idx_i_h].dry = trim_zeros(box.data.dr2t[idx_t_h][idx_i_h].dry)
                print("Done.")  # endregion

                # region ----- Measure oscillations --------------------------------------
                # stat filling the buffer (max 16383 samples per channel)
                print("Measuring oscillation(s)... ", end="")
                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    lockin1.start_filling_buffer()
                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    lockin2.start_filling_buffer()

                # wait for filling lock-in(s) buffer and then retrieve data
                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    lockin1.wait_for_buffer_full(box.settings.lockin1.samples)
                    x1 = lockin1.read_buffer(channel=1, bin_start=0, bin_end=box.settings.lockin1.samples, mode="binary") * np.sqrt(2)
                    y1 = lockin1.read_buffer(channel=2, bin_start=0, bin_end=box.settings.lockin1.samples, mode="binary") * np.sqrt(2)

                    box.data.dr1t[idx_t][idx_i_h].drx_raw = x1 / box.data.i_th_ex
                    box.data.dr1t[idx_t][idx_i_h].dry_raw = y1 / box.data.i_th_ex
                    box.data.dr1t[idx_t][idx_i_h].drx_avg = mean(x1) / box.data.i_th_ex
                    box.data.dr1t[idx_t][idx_i_h].drx_stddev = std(x1) / box.data.i_th_ex
                    box.data.dr1t[idx_t][idx_i_h].dry_avg = mean(y1) / box.data.i_th_ex
                    box.data.dr1t[idx_t][idx_i_h].dry_stddev = std(y1) / box.data.i_th_ex

                    plot1.lndr1x[idx_t_h] = plot1.update(ax=plot1.dr, ln=plot1.lndr1x[idx_t_h], x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1t[idx_t][k].drx_avg for k in range(idx_i_h+1)]), marker="o", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                    plot1.lndr1y[idx_t_h] = plot1.update(ax=plot1.dr, ln=plot1.lndr1y[idx_t_h], x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1t[idx_t][k].dry_avg for k in range(idx_i_h+1)]), marker="o", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                    plot1.lndr1xerr[idx_t_h] = plot1.update(ax=plot1.drerr, ln=plot1.lndr1xerr[idx_t_h], x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1t[idx_t][k].drx_stddev for k in range(idx_i_h+1)]), marker="o", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                    plot1.lndr1yerr[idx_t_h] = plot1.update(ax=plot1.drerr, ln=plot1.lndr1yerr[idx_t_h], x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1t[idx_t][k].dry_stddev for k in range(idx_i_h+1)]), marker="o", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)

                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    lockin2.wait_for_buffer_full(box.settings.lockin2.samples)
                    x2 = lockin2.read_buffer(channel=1, bin_start=0, bin_end=box.settings.lockin2.samples, mode="binary") * np.sqrt(2)
                    y2 = lockin2.read_buffer(channel=2, bin_start=0, bin_end=box.settings.lockin2.samples, mode="binary") * np.sqrt(2)

                    box.data.dr2t[idx_t][idx_i_h].drx_raw = x2 / box.data.i_th_ex
                    box.data.dr2t[idx_t][idx_i_h].dry_raw = y2 / box.data.i_th_ex
                    box.data.dr2t[idx_t][idx_i_h].drx_avg = mean(x2) / box.data.i_th_ex
                    box.data.dr2t[idx_t][idx_i_h].drx_stddev = std(x2) / box.data.i_th_ex
                    box.data.dr2t[idx_t][idx_i_h].dry_avg = mean(y2) / box.data.i_th_ex
                    box.data.dr2t[idx_t][idx_i_h].dry_stddev = std(y2) / box.data.i_th_ex

                    plot1.lndr2x[idx_t_h] = plot1.update(ax=plot1.dr, ln=plot1.lndr2x[idx_t_h], x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2t[idx_t][k].drx_avg for k in range(idx_i_h+1)]), marker="D", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                    plot1.lndr2y[idx_t_h] = plot1.update(ax=plot1.dr, ln=plot1.lndr2y[idx_t_h], x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2t[idx_t][k].dry_avg for k in range(idx_i_h+1)]), marker="D", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                    plot1.lndr2xerr[idx_t_h] = plot1.update(ax=plot1.drerr, ln=plot1.lndr2xerr[idx_t_h], x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2t[idx_t][k].drx_stddev for k in range(idx_i_h+1)]), marker="D", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                    plot1.lndr2yerr[idx_t_h] = plot1.update(ax=plot1.drerr, ln=plot1.lndr2yerr[idx_t_h], x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2t[idx_t][k].dry_stddev for k in range(idx_i_h+1)]), marker="D", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                print("Done.")  # endregion

                # region ----- Ramp down thermometers current ----------------------------
                print("Ramping down thermometer(s) current to 0 A... ", end="")
                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    smu1.sweep_bias("i", box.data.i_th_ex, 0, 100, 10e-6, box.settings.smu1.source_range, "auto", box.settings.smu1.compliance, 0, 20e-3, "local")
                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    smu2.sweep_bias("i", box.data.i_th_ex, 0, 100, 10e-6, box.settings.smu2.source_range, "auto", box.settings.smu2.compliance, 0, 20e-3, "local")
                print("Done")  # endregion

                # region ----- Measure LPF (iv) ------------------------------------------
                print("Measuring low pass filtered component(s)... ", end="")

                for idx_i_th, val_i_th in enumerate(box.data.i_th):

                    if box.data.thermometer == 1 or box.data.thermometer == "both":
                        smu1.set_bias_level(bias=val_i_th, delay=0.1)  # set current off thermometer 1
                        dmm1.send_trigger()  # send trigger to dmm1
                    if box.data.thermometer == 2 or box.data.thermometer == "both":
                        smu2.set_bias_level(bias=val_i_th, delay=0.1)  # set current off thermometer 2
                        dmm2.send_trigger()  # send trigger to dmm2
                    if box.data.thermometer == 1 or box.data.thermometer == "both":
                        dmm1.wait_for_srq()  # wait for srq from dmm1
                        box.data.dr1lpft[idx_t][idx_i_h].v[idx_i_th] = dmm1.read_last()  # read last measurement and store data in array v1
                        dmm1.clear_measurement_event_register()  # clear event register
                    if box.data.thermometer == 2 or box.data.thermometer == "both":
                        dmm2.wait_for_srq()  # wait for srq from dmm2
                        box.data.dr2lpft[idx_t][idx_i_h].v[idx_i_th] = dmm2.read_last()  # read last measurement and store data in array v2
                        dmm2.clear_measurement_event_register()  # clear event register

                # set bias level to 0, switch off smu(s) and multimeter(s)
                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    smu1.set_bias_level(0)
                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    smu2.set_bias_level(0)

                # calculate resistance drift of thermometer 1 and thermometer 2 and update figure
                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    fit1 = scipy.stats.linregress(box.data.dr1lpft[idx_t][idx_i_h].i, box.data.dr1lpft[idx_t][idx_i_h].v)
                    box.data.dr1lpft[idx_t][idx_i_h].r = fit1[0] - box.data.iv1[idx_t].r  # store slope difference
                    box.data.dr1lpft[idx_t][idx_i_h].r_stderr = np.sqrt(fit1[4] ** 2 + box.data.iv1[idx_t].r_stderr ** 2)  # store slope difference standard error

                    plot1.lndr1lpf[idx_t_h] = plot1.update(ax=plot1.drlpf, ln=plot1.lndr1lpf[idx_t_h], x=i_h[0:idx_i_h+1], y=array([box.data.dr1lpft[idx_t_h][idx_i_h].r for x in range(idx_i_h+1)]), marker="o", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                    plot1.lndr1lpferr[idx_t_h] = plot1.update(ax=plot1.drlpferr, ln=plot1.lndr1lpferr[idx_t_h], x=i_h[0:idx_i_h], y=array([box.data.dr1lpft[idx_t_h][idx_i_h].r_stderr for x in range(idx_i_h+1)]), marker="o", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)

                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    fit2 = scipy.stats.linregress(box.data.dr2lpft[idx_t][idx_i_h].i, box.data.dr2lpft[idx_t][idx_i_h].v)
                    box.data.dr2lpft[idx_t][idx_i_h].r = fit2[0] - box.data.iv2[idx_t].r  # store slope difference
                    box.data.dr2lpft[idx_t][idx_i_h].r_stderr = np.sqrt(fit2[4] ** 2 + box.data.iv2[idx_t].r_stderr ** 2)  # store slope difference standard error

                    plot1.lndr2lpf[idx_t_h] = plot1.update(ax=plot1.drlpf, ln=plot1.lndr2lpf[idx_t_h], x=i_h[0:idx_i_h+1], y=array([box.data.dr2lpft[idx_t_h][idx_i_h].r for x in range(idx_i_h+1)]), marker="D", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                    plot1.lndr2lpferr[idx_t_h] = plot1.update(ax=plot1.drlpferr, ln=plot1.lndr2lpferr[idx_t_h], x=i_h[0:idx_i_h+1], y=array([box.data.dr2lpft[idx_t_h][idx_i_h].r_stderr for x in range(idx_i_h+1)]), marker="D", linewidth=0, markerfacecolor=plot1.cm(plot1.norm(val_t)), markeredgecolor="black", alpha=0.5)
                print("Done.")  # endregion

            # region ----- Ramp down heater down ----------------------------------
            print("Ramping down heater current from {} mA to 0 mA... ".format(val_i_h * 1000), end="")
            lockin1.sweep_v(start=val_i_h / box.settings.aiv.gain / np.sqrt(2), stop=0, n_step=1000, rate=10e-6 / box.settings.aiv.gain / np.sqrt(2))
            aiv.operation(input="off", output="on")
            print("Done.")  # endregion

            # region ----- Prompt user -----------------------------------------------
            if box.data.iv_check is False:
                accept = True
                print("Calibration at {} K complete.".format(t))
            elif box.data.iv_check is True:
                accept = None
                while (accept is not True) and (accept is not False):
                    accept = input("Accept calibration and continue measurement? (y/n)")
                    if accept == "y":
                        accept = True
                        print("Calibration accepted. Measurement continues.")
                    elif accept == "n":
                        accept = False
                        input("Calibration rejected. Make the proper adjustments and then press Enter to repeat.")
                    else:
                        accept = None
                        print("Invalid input. Input must be either 'y' (to accept) or 'n' (to reject).")
            # endregion

        idx_t_h = idx_t_h + 1

    # region ----- Save data to disc ----
    print("Saving file(s) to disc... ", end="")
    if os.path.exists(box.filename):
        if os.path.exists(box.backupname):
            os.remove(box.backupname)
        os.rename(box.filename, box.backupname)
    with open(box.filename, "wb") as file:
        pickle.dump(box, file)
    print("Done.")
    plot1.fig.savefig(fname=box.filename + ".png", format="png")
    # endregion

# region ----- Terminate program -----
input("Measurement complete. Ground the device then press Enter to terminate.")

# Switch off instrumentation
if box.data.thermometer == 1 or box.data.thermometer == "both":
    smu1.switch_off()
    dmm1.stop()
if box.data.thermometer == 2 or box.data.thermometer == "both":
    smu2.switch_off()
    dmm2.stop()

# turn interactive mode off and plot
plt.show()
# endregion
