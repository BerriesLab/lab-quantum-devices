# region ----- Import packages -----
import keithley_dmm2182a
import srs_sr830
import srs_srcs580
import lakeshore_tc336
import oxford_mercury_itc
import pyvisa
import scipy.stats
import os
import numpy as np
from numpy import mean, std, floor
import pickle
from Objects.Backup.measurement_objects import *
from Objects.Backup.plot_objects import *
import time

# endregion

#######################################################################
#   Author:         Davide Beretta
#   Date:           11.05.2021
#   Description:    TE-FET: calibration (for Stanford cs580)
#######################################################################

# region ----- measurement(s) options --------------------------------------------------------------------------------------------------------------------------
box = experiment()
box.main = r"E:\Samples"
box.date = datetime.datetime.now()
box.filename = "{} - calibration".format(box.date.strftime("%Y.%m.%d %H.%M.%S"))
box.backupname = box.filename + ".bak"
box.experiment = "calibration"
box.chip = "tep_b_2"
box.device = "c7"
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
box.data = calibration()
box.data.thermometer = "both"                   # [string or int] select the thermometer to calibrate: "1" (int), "2" (int), or "both" (string)
box.data.heater = 1                             # [int] select heater in use (it has no practical effect on the code)
box.data.t = linspace(99, 105, 31)              # [1D array] temperatures (in K).
box.data.i_h = linspace(0e-3, 3e-3, 7)          # [1D array] heater current (in A).
box.data.t_h = array([100])                     # [1D array] temperatures (in K) where heater calibration occurs. Pass an empty array to skip.
box.data.i_th = linspace(0, 50e-6, 21)          # [1D array] "forward" thermometer current for iv (in A).
box.data.i_th_ex = 50e-6                        # [float] thermometer excitation current
box.data.i2doublesweepi()
box.data.generate_measurements()
# endregion ----------------------------------------------------------------------------------------------------------------------------------------------------

# region ----- Settings ------
# ----- tc settings -----
box.settings.__setattr__("tc", empty())
box.settings.tc.address = "ASRL4::INSTR"        # [string] address of temperature controller
box.settings.tc.model = 1                       # [string] select tc_model (0: lakeshore 336, 1: oxford mercury itc)
box.settings.tc.t_switch = 50                   # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium"
box.settings.tc.sampling_freq_plot = 2          # [int] temperature sampling frequency (in Hz)
box.settings.tc.settling_time = 15 * 60         # [float] cryostat thermalization time (in s).
box.settings.tc.settling_time_init = 60 * 60    # [float] cryostat initial thermalization time (in s).
box.settings.tc.dt_lift = np.inf                # [float] temperature interval in between needles lifting (in K). Note: set to inf for Heliox
# ----- src1 settings -----
box.settings.__setattr__("src1", empty())
box.settings.src1.address = "xxx"               # [string] address of aiv
box.settings.src1.gain = 100e-6                 # [float] gain (in A/V)
box.settings.src1.isolation = "float"           # [string] isolation
box.settings.src1.shield = "return"             # [string] shield
box.settings.src1.compliance = 50               # [float] compliance (in V)
box.settings.src1.response = "slow"             # [string] response
box.settings.src1.delay = 0.1                   # [string] current source settling time (in s)
box.settings.src1.rate = 10e-6                  # [float] current sweep rate (in A/s). Used in current sweep.
box.settings.src1.step = 1e-6                   # [float] current step (in A). Used in current sweep.
# ----- src2 settings -----
box.settings.__setattr__("src2", empty())
box.settings.src2.address = "xxx"               # [string] address of aiv
box.settings.src2.gain = box.settings.src1.gain  # [float] gain (in A/V)
box.settings.src2.isolation = box.settings.src1.isolation  # [string] isolation
box.settings.src2.shield = box.settings.src1.shield  # [string] shield
box.settings.src2.compliance = box.settings.src1.compliance  # [float] compliance (in V))
box.settings.src2.response = box.settings.src1.response  # [string] response
box.settings.src2.delay = box.settings.src1.delay  # [string] current source settling time (in s)
box.settings.src2.step = box.settings.src1.step  # [float] current step (in A). Used in current sweep.
# ----- dmm1 settings -----
box.settings.__setattr__("dmm1", empty())
box.settings.dmm1.address = "GPIB0::3"          # [string] address of dmm 1
box.settings.dmm1.nplc = 1                      # [float] nplc
box.settings.dmm1.sense_range = 10e-3           # [float] range
box.settings.dmm1.digital_samples = 1           # [int] digital averaged samples (1 - 9999)
box.settings.dmm1.lpf = "on"                    # [string] low pass filter status (cutoff frequency at 18 Hz)
# ----- dmm2 settings -----
box.settings.__setattr__("dmm2", empty())
box.settings.dmm2.address = "GPIB0::4"          # [string] address of dmm 2
box.settings.dmm2.nplc = box.settings.dmm1.nplc  # [float] nplc
box.settings.dmm2.sense_range = box.settings.dmm1.sense_range  # [float] range
box.settings.dmm2.digital_samples = box.settings.dmm1.digital_samples  # [int] digital averaged samples (1 - 9999)
box.settings.dmm2.lpf = box.settings.dmm1.lpf  # [string] low pass filter status (cutoff frequency at 18 Hz)
# ----- lock-in1 settings -----
box.settings.__setattr__("lockin1", empty())
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
box.settings.lockin1.settling_time = 3 * 60     # [float] heater thermalization time (in s)
box.settings.lockin1.rate = 10e-6               # [float] amplitude sweep rate (in A/s). Used in heater current amplitude sweeps.
box.settings.lockin1.step = 1e-6                # [float] amplitude step (in A). Used in heater current amplitude sweeps.
# ----- lock-in2 settings -----
box.settings.__setattr__("lockin2", empty())
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
box.settings.__setattr__("aiv", empty())
box.settings.aiv.address = "ASRL2::INSTR"       # [string] address of aiv
box.settings.aiv.gain = 10e-3                   # [float] set the gain of the voltage controlled current amplifier
box.settings.aiv.isolation = "float"            # [string] isolation
box.settings.aiv.shield = "return"              # [string] shield
box.settings.aiv.compliance = 50                # [float] set the compliance to the highest level
box.settings.aiv.response = "fast"              # [string] set the response
# endregion

# region ----- Read resources and create instrumentation objects -----
print("\n***** Loading instrumentation drivers *****")

rm = pyvisa.ResourceManager()

src1 = srs_srcs580.srcs580(visa=rm.open_resource(box.settings.src1.address))
print("Found smu 1: {}".format(src1.model))

src2 = srs_srcs580.srcs580(visa=rm.open_resource(box.settings.src2.address))
print("Found smu 1: {}".format(src2.model))

dmm1 = keithley_dmm2182a.dmm2182a(visa=rm.open_resource(box.settings.dmm1.address))
print("Found dmm 1: {}".format(dmm1.model))

dmm2 = keithley_dmm2182a.dmm2182a(visa=rm.open_resource(box.settings.dmm2.address))
print("Found dmm 2: {}".format(dmm2.model))

lockin1 = srs_sr830.sr830(visa=rm.open_resource(box.settings.lockin1.address))
print("Found lock-in 1: {}".format(lockin1.model))

lockin2 = srs_sr830.sr830(visa=rm.open_resource(box.settings.lockin2.address))
print("Found lock-in 2: {}".format(lockin2.model))

aiv = srs_srcs580.srcs580(visa=rm.open_resource(box.settings.aiv.address))
print("Found I/V current amplifier: {}".format(aiv.model))

if box.settings.tc.model == 0:
    tc = lakeshore_tc336.tc336(visa=rm.open_resource(box.settings.tc.address))
    print("Found temperature controller: {}".format(tc.model))
elif box.settings.tc.model == 1:
    tc = oxford_mercury_itc.mercuryitc(visa=rm.open_resource(box.settings.tc.address))
    print("Found temperature controller: {}".format(tc.model))
else:
    raise ValueError("Temperature controller ID does not belong to the list of the accepted values.")
# endregion

# region ----- Estimate measurement time -----
estimated_time_to_lift = (box.settings.tc.dt_lift / (box.data.t[1]-box.data.t[0])) * box.settings.tc.settling_time
estimated_measurement_time = box.settings.tc.settling_time_init + len(box.data.t) * box.settings.tc.settling_time +\
                             len(box.data.t_h) * len(box.data.i_h) * box.settings.lockin1.settling_time
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
if abs(box.data.t.max() - box.data.t.min()) > box.settings.tc.dt_lift:
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
src1.configure(box.settings.src1.gain, box.settings.src1.response, box.settings.src1.shield, box.settings.src1.isolation,
               "off", "on", box.settings.src1.compliance)
src2.configure(box.settings.src2.gain, box.settings.src2.response, box.settings.src2.shield, box.settings.src2.isolation,
               "off", "on", box.settings.src2.compliance)
dmm1.configure(box.settings.dmm1.lpf, box.settings.dmm1.digital_samples, box.settings.dmm1.sense_range,
               box.settings.dmm1.nplc, "bus", "inf", "default", "on", "off")  # load reading program in dmm 1
dmm2.configure(box.settings.dmm2.lpf, box.settings.dmm2.digital_samples, box.settings.dmm2.sense_range,
               box.settings.dmm2.nplc, "bus", "inf", "default", "on", "off")  # load reading program in dmm 2
print("Done.")
# endregion

# region ----- Initialize figures -----
print("Initializing figure... ", end="")
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
plot1 = plot_calibration(box.data)
plot2 = plot_obst(["stage", "shield"], box.settings.tc.settling_time)
plot3 = plot_obst(["x1", "y1", "x2", "y2"], box.settings.lockin1.settling_time)
plt.show(block=False)
plt.pause(.1)
print("Done.")  # endregion

input("Unground the device, then press Enter to start measurement...")
# set the temperature at which needles must be lifted and then lowered again before continuing
t_lift = box.data.t.min() + box.settings.tc.dt_lift

idx_t_h = 0
for idx_t, val_t in enumerate(box.data.t):

    # region ----- Lift needles if needed -----
    if val_t > t_lift:  # check if user must lift needles
        input("Please ground the device, lift and then lower the probes back into position. "
              "Then unground the device and press Enter to continue...")
        t_lift = val_t + box.settings.tc.dt_lift  # update temperature lift value
    # endregion

    # region ----- Set temperature and wait for thermalization -----
    tc.set_temperature(output=0, setpoint=val_t)
    tc.set_temperature(output=1, setpoint=val_t) if box.settings.tc.model == 0 else None

    print("Waiting for thermalization at {:04.1f} K...".format(val_t), end="")
    settling_time = box.settings.tc.settling_time_init if idx_t == 0 else box.settings.tc.settling_time
    box.data.tt[idx_t].setpoint = val_t
    box.data.tt[idx_t].time = zeros(int(ceil(settling_time * box.settings.tc.sampling_freq_plot)))
    box.data.tt[idx_t].stage = zeros(int(ceil(settling_time * box.settings.tc.sampling_freq_plot)))
    box.data.tt[idx_t].shield = zeros(int(ceil(settling_time * box.settings.tc.sampling_freq_plot)))

    k = 0
    t0 = time.time()
    plot2.ax.set_xlim([0, settling_time])
    plot2.ax.lines[3].set_data(x=array([0, settling_time]), y=array([val_t, val_t]))
    while time.time() - t0 <= settling_time:
        box.data.tt[idx_t].time[k] = time.time() - t0
        box.data.tt[idx_t].stage[k] = tc.read_temperature("a")
        box.data.tt[idx_t].shield[k] = tc.read_temperature("b")
        plot2.ax.lines[0].set_data(x=box.data.tt[idx_t].time[0:k+1], y=box.data.tt[idx_t].stage[0:k+1])
        plot2.ax.lines[1].set_data(x=box.data.tt[idx_t].time[0:k+1], y=box.data.tt[idx_t].shield[0:k+1])
        plt.pause(1 / box.settings.tc.sampling_freq_plot)
        k = k + 1
    plot2.fig.savefig(fname=box.filename + " - thermalization at {} K.png".format(val_t), format="png")
    print("Done.")

    # remove trailing zeros from arrays
    box.data.tt[idx_t].time = box.data.tt[idx_t].time[0:k]
    box.data.tt[idx_t].temperature_stage = box.data.tt[idx_t].temperature_stage[0:k]
    box.data.tt[idx_t].temperature_shield = box.data.tt[idx_t].temperature_shield[0:k]

    # endregion

    # region ----- Allocate RAM ----------------------------------------------
    if box.data.thermometer == 1 or box.data.thermometer == "both":
        box.data.iv1[idx_t].temperature = val_t
        box.data.iv1[idx_t].i = box.data.i_th
        box.data.iv1[idx_t].v = zeros(len(box.data.i_th))
    if box.data.thermometer == 2 or box.data.thermometer == "both":
        box.data.iv2[idx_t].temperature = val_t
        box.data.iv2[idx_t].i = box.data.i_th
        box.data.iv2[idx_t].v = zeros(len(box.data.i_th))
    # endregion

    # region ----- Make iv ---------------------------------------------------
    print("Making iv(s)... ", end="")

    # measure
    for idx_i_th, val_i_th in enumerate(box.data.i_th):

        if box.data.thermometer == 1 or box.data.thermometer == "both":
            src1.set_current(value=val_i_th, delay=box.settings.src1.delay)
            dmm1.send_trigger()

        if box.data.thermometer == 2 or box.data.thermometer == "both":
            src2.set_current(value=val_i_th, delay=box.settings.src2.delay)
            dmm2.send_trigger()

        if box.data.thermometer == 1 or box.data.thermometer == "both":
            dmm1.wait_for_srq()
            box.data.iv1[idx_t].v[idx_i_th] = dmm1.read_last()
            dmm1.clear_measurement_event_register()
            plot1.iv1.lines[idx_t].set_data(box.data.iv1[idx_t].i[0:idx_i_th+1], box.data.iv1[idx_t].v[0:idx_i_th+1])

        if box.data.thermometer == 2 or box.data.thermometer == "both":
            dmm2.wait_for_srq()
            box.data.iv2[idx_t].v[idx_i_th] = dmm2.read_last()
            dmm2.clear_measurement_event_register()
            plot1.iv2.lines[idx_t].set_data(box.data.iv2[idx_t].i[0:idx_i_th+1], box.data.iv2[idx_t].v[0:idx_i_th+1])

        plt.pause(0.001)

    # set bias level to 0
    if box.data.thermometer == 1 or box.data.thermometer == "both":
        src1.set_current(value=0)
    if box.data.thermometer == 2 or box.data.thermometer == "both":
        src2.set_current(value=0)

    # calculate resistance of thermometer 1 and thermometer 2 and update plots
    if box.data.thermometer == 1 or box.data.thermometer == "both":
        fit1 = scipy.stats.linregress(box.data.iv1[idx_t].i, box.data.iv1[idx_t].v)
        box.data.iv1[idx_t].r = fit1[0]
        box.data.iv1[idx_t].r_stderr = fit1[4]
        plot1.rt.lines[2*idx_t].set_data(x=box.data.t[0: idx_t+1], y=array([box.data.iv1[k].r for k in range(idx_t+1)]))
        plot1.rterr.lines[2*idx_t].set_data(x=box.data.t[0: idx_t+1], y=array([box.data.iv1[k].r_stderr for k in range(idx_t+1)]))

    if box.data.thermometer == 2 or box.data.thermometer == "both":
        fit2 = scipy.stats.linregress(box.data.iv2[idx_t].i, box.data.iv2[idx_t].v)
        box.data.iv2[idx_t].r = fit2[0]
        box.data.iv2[idx_t].r_stderr = fit2[4]
        plot1.rt.lines[2*idx_t+1].set_data(x=box.data.t[0: idx_t+1], y=array([box.data.iv2[k].r for k in range(idx_t+1)]))
        plot1.rterr.lines[2*idx_t+1].set_data(x=box.data.t[0: idx_t+1], y=array([box.data.iv2[k].r_stderr for k in range(idx_t+1)]))

    plt.pause(0.001)
    # endregion

    if val_t in box.data.t_h:

        print("Starting heater calibration at {} K...".format(val_t))

        for idx_i_h, val_i_h in enumerate(box.data.i_h):

            # region ----- Allocate RAM ----------------------------------------------
            print("Allocating RAM... ", end="")
            if box.data.thermometer == 1 or box.data.thermometer == "both":
                box.data.dr1t[idx_t_h][idx_i_h].temperature = val_t
                box.data.dr1t[idx_t_h][idx_i_h].i_h = val_i_h
                box.data.dr1t[idx_t_h][idx_i_h].time = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.dr1t[idx_t_h][idx_i_h].drx = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.dr1t[idx_t_h][idx_i_h].dry = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.dr1t[idx_t_h][idx_i_h].drx_raw = zeros(box.settings.lockin1.samples)
                box.data.dr1t[idx_t_h][idx_i_h].dry_raw = zeros(box.settings.lockin1.samples)
                box.data.dr1lpft[idx_t_h][idx_i_h].i = box.data.i_th
                box.data.dr1lpft[idx_t_h][idx_i_h].v = zeros(len(box.data.i_th))

            if box.data.thermometer == 2 or box.data.thermometer == "both":
                box.data.dr2t[idx_t_h][idx_i_h].temperature = val_t
                box.data.dr2t[idx_t_h][idx_i_h].i_h = val_i_h
                box.data.dr2t[idx_t_h][idx_i_h].temperature = val_t
                box.data.dr2t[idx_t_h][idx_i_h].time = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.dr2t[idx_t_h][idx_i_h].drx = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.dr2t[idx_t_h][idx_i_h].dry = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.dr2t[idx_t_h][idx_i_h].drx_raw = zeros(box.settings.lockin2.samples)
                box.data.dr2t[idx_t_h][idx_i_h].dry_raw = zeros(box.settings.lockin2.samples)
                box.data.dr2lpft[idx_t_h][idx_i_h].i = box.data.i_th
                box.data.dr2lpft[idx_t_h][idx_i_h].v = zeros(len(box.data.i_th))

            print("Done.")  # endregion

            # region ----- Ramp up thermometers current ------------------------------
            print("Ramping up thermometer(s) current to {} A... ".format(box.data.i_th_ex), end="")
            if box.data.thermometer == 1 or box.data.thermometer == "both":
                src1.sweep_current(start=0,
                                   stop=box.data.i_th_ex,
                                   nstep=int(floor(box.data.i_th_ex / box.settings.src1.step)),
                                   rate=box.settings.src1.rate)
            if box.data.thermometer == 2 or box.data.thermometer == "both":
                src2.sweep_current(start=0,
                                   stop=box.data.i_th_ex,
                                   nstep=int(floor(box.data.i_th_ex / box.settings.src2.step)),
                                   rate=box.settings.src2.rate)
            print("Done.")  # endregion ----------------------------------------------

            # region ----- Ramp up heater current ------------------------------------
            print("Ramping up heater current to {:.1f} mA... ".format(val_i_h * 1000), end="")
            if val_i_h / box.settings.aiv.gain < 0.004:
                aiv.operation(input="off", output="on")
            else:
                aiv.operation(input="on", output="on")

            if idx_i_h == 0:
                i_h_ = 0
            else:
                i_h_ = box.data.i_h[idx_i_h-1]

            lockin1.sweep_v(start=i_h_ / box.settings.aiv.gain / np.sqrt(2),
                            stop=val_i_h / box.settings.aiv.gain / np.sqrt(2),
                            n_step=int(floor(abs((val_i_h - i_h_) / box.settings.lockin1.step))),
                            rate=box.settings.lockin1.rate / box.settings.aiv.gain / np.sqrt(2))
            print("Done.")  # endregion

            # region ----- Wait for steady state -------------------------------------
            t0 = time.time()
            print("Waiting for thermalization... ", end="")
            idx = 0
            while time.time() - t0 <= box.settings.lockin1.settling_time:

                if box.data.thermometer == 1 or "both":
                    temp1, temp2 = lockin1.read()
                    box.data.dr1t[idx_t_h][idx_i_h].time[idx] = time.time() - t0
                    box.data.dr1t[idx_t_h][idx_i_h].drx[idx] = temp1 * np.sqrt(2) / box.data.i_th_ex
                    box.data.dr1t[idx_t_h][idx_i_h].dry[idx] = temp2 * np.sqrt(2) / box.data.i_th_ex
                    plot3.ax.lines[0].set_data(x=box.data.dr1t[idx_t_h][idx_i_h].time[0:idx+1], y=box.data.dr1t[idx_t_h][idx_i_h].drx[0:idx+1])
                    plot3.ax.lines[1].set_data(x=box.data.dr1t[idx_t_h][idx_i_h].time[0:idx+1], y=box.data.dr1t[idx_t_h][idx_i_h].dry[0:idx+1])

                if box.data.thermometer == 2 or "both":
                    temp1, temp2 = lockin2.read()
                    box.data.dr2t[idx_t_h][idx_i_h].time[idx] = time.time() - t0
                    box.data.dr2t[idx_t_h][idx_i_h].drx[idx] = temp1 * np.sqrt(2) / box.data.i_th_ex
                    box.data.dr2t[idx_t_h][idx_i_h].dry[idx] = temp2 * np.sqrt(2) / box.data.i_th_ex
                    plot3.ax.lines[2].set_data(x=box.data.dr2t[idx_t_h][idx_i_h].time[0:idx+1], y=box.data.dr2t[idx_t_h][idx_i_h].drx[0:idx+1])
                    plot3.ax.lines[3].set_data(x=box.data.dr2t[idx_t_h][idx_i_h].time[0:idx+1], y=box.data.dr2t[idx_t_h][idx_i_h].dry[0:idx+1])

                plt.pause(1 / box.settings.lockin1.sampling_freq_plot)
                idx = idx + 1

            plot3.fig.savefig(fname=box.filename + " - thermalization at {} K and {:.1f} mA.png".format(val_t, val_i_h*1000), format="png")

            # remove trailing zeros from arrays
            box.data.dr1t[idx_t_h][idx_i_h].time = box.data.dr1t[idx_t_h][idx_i_h].time[0:idx]
            box.data.dr1t[idx_t_h][idx_i_h].drx = box.data.dr1t[idx_t_h][idx_i_h].drx[0:idx]
            box.data.dr1t[idx_t_h][idx_i_h].dry = box.data.dr1t[idx_t_h][idx_i_h].dry[0:idx]
            box.data.dr2t[idx_t_h][idx_i_h].time = box.data.dr2t[idx_t_h][idx_i_h].time[0:idx]
            box.data.dr2t[idx_t_h][idx_i_h].drx = box.data.dr2t[idx_t_h][idx_i_h].drx[0:idx]
            box.data.dr2t[idx_t_h][idx_i_h].dry = box.data.dr2t[idx_t_h][idx_i_h].dry[0:idx]
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

                box.data.dr1t[idx_t_h][idx_i_h].drx_raw = x1 / box.data.i_th_ex
                box.data.dr1t[idx_t_h][idx_i_h].dry_raw = y1 / box.data.i_th_ex
                box.data.dr1t[idx_t_h][idx_i_h].drx_avg = mean(x1) / box.data.i_th_ex
                box.data.dr1t[idx_t_h][idx_i_h].drx_stddev = std(x1) / box.data.i_th_ex
                box.data.dr1t[idx_t_h][idx_i_h].dry_avg = mean(y1) / box.data.i_th_ex
                box.data.dr1t[idx_t_h][idx_i_h].dry_stddev = std(y1) / box.data.i_th_ex

                plot1.drx.lines[2*idx_t_h].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1t[idx_t_h][k].drx_avg for k in range(idx_i_h+1)]))
                plot1.dry.lines[2*idx_t_h].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1t[idx_t_h][k].dry_avg for k in range(idx_i_h+1)]))
                plot1.drxerr.lines[2*idx_t_h].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1t[idx_t_h][k].drx_stddev for k in range(idx_i_h+1)]))
                plot1.dryerr.lines[2*idx_t_h].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1t[idx_t_h][k].dry_stddev for k in range(idx_i_h+1)]))

            if box.data.thermometer == 2 or box.data.thermometer == "both":
                lockin2.wait_for_buffer_full(box.settings.lockin2.samples)
                x2 = lockin2.read_buffer(channel=1, bin_start=0, bin_end=box.settings.lockin2.samples, mode="binary") * np.sqrt(2)
                y2 = lockin2.read_buffer(channel=2, bin_start=0, bin_end=box.settings.lockin2.samples, mode="binary") * np.sqrt(2)

                box.data.dr2t[idx_t_h][idx_i_h].drx_raw = x2 / box.data.i_th_ex
                box.data.dr2t[idx_t_h][idx_i_h].dry_raw = y2 / box.data.i_th_ex
                box.data.dr2t[idx_t_h][idx_i_h].drx_avg = mean(x2) / box.data.i_th_ex
                box.data.dr2t[idx_t_h][idx_i_h].drx_stddev = std(x2) / box.data.i_th_ex
                box.data.dr2t[idx_t_h][idx_i_h].dry_avg = mean(y2) / box.data.i_th_ex
                box.data.dr2t[idx_t_h][idx_i_h].dry_stddev = std(y2) / box.data.i_th_ex

                plot1.drx.lines[2*idx_t_h+1].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2t[idx_t_h][k].drx_avg for k in range(idx_i_h+1)]))
                plot1.dry.lines[2*idx_t_h+1].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2t[idx_t_h][k].dry_avg for k in range(idx_i_h+1)]))
                plot1.drxerr.lines[2*idx_t_h+1].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2t[idx_t_h][k].drx_stddev for k in range(idx_i_h+1)]))
                plot1.dryerr.lines[2*idx_t_h+1].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2t[idx_t_h][k].dry_stddev for k in range(idx_i_h+1)]))

            plt.pause(0.001)
            print("Done.")  # endregion

            # region ----- Ramp down thermometers current ----------------------------
            print("Ramping down thermometer(s) current to 0 A... ", end="")
            if box.data.thermometer == 1 or box.data.thermometer == "both":
                src1.sweep_current(start=box.data.i_th_ex,
                                   stop=0,
                                   nstep=int(floor(box.data.i_th_ex / box.settings.src1.step)),
                                   rate=box.settings.src1.rate)
            if box.data.thermometer == 2 or box.data.thermometer == "both":
                src2.sweep_current(start=box.data.i_th_ex,
                                   stop=0,
                                   nstep=int(floor(box.data.i_th_ex / box.settings.src2.step)),
                                   rate=box.settings.src2.rate)
            print("Done")  # endregion

            # region ----- Measure LPF (iv) ------------------------------------------
            print("Measuring low pass filtered component(s)... ", end="")

            for idx_i_th, val_i_th in enumerate(box.data.i_th):

                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    src1.set_current(value=val_i_th, delay=box.settings.src1.delay)  # set current off thermometer 1
                    dmm1.send_trigger()  # send trigger to dmm1
                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    src2.set_current(value=val_i_th, delay=box.settings.src2.delay)  # set current off thermometer 1
                    dmm2.send_trigger()  # send trigger to dmm2
                if box.data.thermometer == 1 or box.data.thermometer == "both":
                    dmm1.wait_for_srq()  # wait for srq from dmm1
                    box.data.dr1lpft[idx_t_h][idx_i_h].v[idx_i_th] = dmm1.read_last()  # read last measurement and store data in array v1
                    dmm1.clear_measurement_event_register()  # clear event register
                if box.data.thermometer == 2 or box.data.thermometer == "both":
                    dmm2.wait_for_srq()  # wait for srq from dmm2
                    box.data.dr2lpft[idx_t_h][idx_i_h].v[idx_i_th] = dmm2.read_last()  # read last measurement and store data in array v2
                    dmm2.clear_measurement_event_register()  # clear event register

            # set thermometer current level to 0
            if box.data.thermometer == 1 or box.data.thermometer == "both":
                src1.set_current(value=0)
            if box.data.thermometer == 2 or box.data.thermometer == "both":
                src2.set_current(value=0)

            # calculate resistance drift of thermometer 1 and thermometer 2 and update figure
            if box.data.thermometer == 1 or box.data.thermometer == "both":
                fit1 = scipy.stats.linregress(box.data.dr1lpft[idx_t_h][idx_i_h].i, box.data.dr1lpft[idx_t_h][idx_i_h].v)
                box.data.dr1lpft[idx_t_h][idx_i_h].r = fit1[0] - box.data.iv1[idx_t].r  # store slope difference
                box.data.dr1lpft[idx_t_h][idx_i_h].r_stderr = np.sqrt(fit1[4] ** 2 + box.data.iv1[idx_t].r_stderr ** 2)  # store slope difference stderr

                plot1.drlpf.lines[2*idx_t_h].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1lpft[idx_t_h][idx_i_h].r for x in range(idx_i_h+1)]))
                plot1.drlpferr.lines[2*idx_t_h].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr1lpft[idx_t_h][idx_i_h].r_stderr for x in range(idx_i_h+1)]))

            if box.data.thermometer == 2 or box.data.thermometer == "both":
                fit2 = scipy.stats.linregress(box.data.dr2lpft[idx_t_h][idx_i_h].i, box.data.dr2lpft[idx_t_h][idx_i_h].v)
                box.data.dr2lpft[idx_t_h][idx_i_h].r = fit2[0] - box.data.iv2[idx_t].r  # store slope difference
                box.data.dr2lpft[idx_t_h][idx_i_h].r_stderr = np.sqrt(fit2[4] ** 2 + box.data.iv2[idx_t].r_stderr ** 2)  # store slope difference stderr

                plot1.drlpf.lies[2*idx_t_h+1].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2lpft[idx_t_h][idx_i_h].r for x in range(idx_i_h+1)]))
                plot1.drlpferr.lines[2*idx_t_h+1].set_data(x=box.data.i_h[0:idx_i_h+1], y=array([box.data.dr2lpft[idx_t_h][idx_i_h].r_stderr for x in range(idx_i_h+1)]))

            plt.pause(0.001)
            print("Done.")  # endregion

        # region ----- Ramp down heater current ----------------------------------
        print("Ramping down heater current from {} mA to 0 mA... ".format(val_i_h * 1000), end="")
        lockin1.sweep_v(start=val_i_h / box.settings.aiv.gain / np.sqrt(2),
                        stop=0,
                        n_step=int(floor(abs(val_i_h / box.settings.lockin1.step))),
                        rate=box.settings.lockin1.rate / box.settings.aiv.gain / np.sqrt(2))
        aiv.operation(input="off",
                      output="on")
        print("Done.")  # endregion

        idx_t_h = idx_t_h + 1

    # region ----- Save data to disc --------------------------------------
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

# region ----- Terminate program ---------------------------------------
input("Measurement complete. Ground the device then press Enter to terminate.")
# Switch off instrumentation
if box.data.thermometer == 1 or box.data.thermometer == "both":
    src1.set_output_state("off")
    dmm1.stop()
if box.data.thermometer == 2 or box.data.thermometer == "both":
    src2.set_output_state("off")
    dmm2.stop()
plt.show()  # endregion
