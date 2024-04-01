# region ----- Import packages -----
import srs_sr830
import srs_srcs580
import srs_srdc205
import keithley_smu236
import lakeshore_tc336
import oxford_mercury_itc
import pyvisa
import os
import numpy as np
from numpy import floor
import pickle
from Objects.Backup.measurement_objects import *
from Objects.Backup.plot_objects import *
import time
# endregion

#######################################################################
#   Author:         Davide Beretta
#   Date:           11.05.2021
#   Description:    TE-FET: stability diagram (for Stanford cs580)
#######################################################################

# region ----- measurement(s) options --------------------------------------------------------------------------------------------------------------------------
box = experiment()
box.date = datetime.datetime.now()
box.measurement = "stability diagram"
box.chip = "tep_b_2"
box.device = "c7"
box.main = r"E:\Samples"
box.filename = "{} - te stability diagram".format(box.date.strftime("%Y.%m.%d %H.%M.%S"))
box.backupname = box.filename + ".bak"
# ---------------------------------------
mode = 0                               # [int] select method. 0: highly resistive samples (2 lock-in), 1: low resistive samples (3 lock-in)
heater = 1                             # [int] select heater in use (it has no practical effect on the code)
t = array([100])                       # [1D array] temperatures (in K).
i = array([2.5e-3])                     # [1D array] heater current (in A).
vb = linspace(-1, 1, 21)
vg = linspace(-100, 100, 401)
v = 10e-3                               # [float] amplitude of the dc bias oscillations
# endregion

# region ----- Settings -----------------------------------
# ----- tc settings -----
box.settings.__setattr__("tc", empty())
box.settings.tc.address = "ASRL4::INSTR"        # [string] address of temperature controller
box.settings.tc.model = 1                       # [string] select tc_model (0: lakeshore 336, 1: oxford mercury itc)
box.settings.tc.t_switch = 50                   # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium"
box.settings.tc.sampling_freq_plot = 2          # [int] temperature sampling frequency (in Hz)
box.settings.tc.settling_time = 15 * 60
# ----- dc source -----
box.settings.__setattr__("src1", empty())
box.settings.src.address = "USB::8"            # [string] bias voltage source address
box.settings.src.range = 10e-3                 # [float] bias voltage source range
box.settings.src.isolation = "float"
box.settings.src.sensing = "local"
box.settings.src.rate = 10e-3                   # [float] voltage sweep rate (in V/s)
box.settings.src.step = 1e-3                    # [float] voltage step size (in V)
# ----- lock-in1 settings -----
box.settings.__setattr__("lockin1", empty())
box.settings.lockin1.address = "GPIB0::6"       # [string] address of lockin 1
box.settings.lockin1.reference = "internal"     # [string] reference for frequency
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
box.settings.lockin1.rate = 10e-6               # [float] amplitude sweep rate (A/s). Used in heater current amplitude sweeps.
box.settings.lockin1.step = 1e-6                # [float] amplitude step (in A). Used in heater current amplitude sweeps.
box.settings.lockin1.settling_time_i = 3 * 60   # [float] current settling time (in s)
box.settings.lockin1.settling_time_vb = 1 * 60  # [float] voltage settling time (in s)
box.settings.lockin1.settling_time_vg = 1 * 60  # [float] voltage settling time (in s)
# ----- lock-in2 settings -----
box.settings.__setattr__("lockin2", empty())
box.settings.lockin2.address = "GPIB0::11"      # [string] address of lockin 2
box.settings.lockin2.reference = "internal"
<<<<<<< HEAD
<<<<<<< HEAD
box.settings.lockin2.amplitude = box.data.v / sqrt(2)  # [float] voltage output (G*v should be approx equal to G*alpha*dT)
=======
box.settings.lockin2.amplitude = v / sqrt(2)         # [float] voltage output (G*v should be approx equal to G*alpha*dT)
>>>>>>> parent of 8aa3456 (major2)
=======
box.settings.lockin2.amplitude = v / sqrt(2)         # [float] voltage output (G*v should be approx equal to G*alpha*dT)
>>>>>>> parent of 8aa3456 (major2)
box.settings.lockin2.freq = 2.163 * box.settings.lockin1.freq  # [float] excitation current frequency (in Hz)
box.settings.lockin2.sampling_freq_plot = box.settings.lockin1.sampling_freq_plot
box.settings.lockin2.sampling_freq = box.settings.lockin1.sampling_freq
box.settings.lockin2.samples = box.settings.lockin1.samples
box.settings.lockin2.shield = "float"           # [string] shield ca nbe floating or shorted
box.settings.lockin2.coupling = "ac"            # [string] coupling can be ac or dc
box.settings.lockin2.time = box.settings.lockin1.time  # [float] integration time
box.settings.lockin2.filter = "24 dB/oct"       # [string] filter
box.settings.lockin2.input = "a-b"              # [string] input can be single ended or differential
box.settings.lockin2.sensitivity = "20 uV/pA"   # [string] sensitivity. The "/" is not a division symbols but stands for either Volts or Amperes.
box.settings.lockin2.harmonic = 1               # [int] demodulated harmonic
box.settings.lockin2.reserve = "normal"         # [string] reserve
box.settings.lockin2.rate = 1e-3                # [float] amplitude sweep rate (V/s). Used in amplitude sweeps.
box.settings.lockin2.step = 10e-3               # [float] amplitude step (in V). Used in amplitude sweeps.
box.settings.lockin2.settling_time_i = box.settings.lockin1.settling_time_i
box.settings.lockin2.settling_time_vb = box.settings.lockin1.settling_time_vb
box.settings.lockin2.settling_time_vg = box.settings.lockin1.settling_time_vg
# ----- lock-in3 settings -----
<<<<<<< HEAD
<<<<<<< HEAD
if box.data.mode == 1:
    box.settings.__setattr__("lockin3", empty())
    box.settings.lockin3.address = "GPIB0::13"      # [string] address of lockin 3
    box.settings.lockin3.reference = "external"
    box.settings.lockin3.sampling_freq_plot = box.settings.lockin1.sampling_freq_plot
    box.settings.lockin3.sampling_freq = box.settings.lockin1.sampling_freq
    box.settings.lockin3.samples = box.settings.lockin1.samples
    box.settings.lockin3.shield = "float"           # [string] shield ca nbe floating or shorted
    box.settings.lockin3.coupling = "ac"            # [string] coupling can be ac or dc
    box.settings.lockin3.time = box.settings.lockin1.time  # [float] integration time
    box.settings.lockin3.filter = "24 dB/oct"       # [string] filter
    box.settings.lockin3.input = "a-b"              # [string] input can be single ended or differential
    box.settings.lockin3.sensitivity = "20 uV/pA"   # [string] sensitivity. The "/" is not a division symbols but stands for either Volts or Amperes.
    box.settings.lockin3.harmonic = 1               # [int] demodulated harmonic
    box.settings.lockin3.reserve = "normal"         # [string] reserve
    box.settings.lockin3.settling_time_i = box.settings.lockin1.settling_time_i
    box.settings.lockin3.settling_time_vb = box.settings.lockin1.settling_time_vb
    box.settings.lockin3.settling_time_vg = box.settings.lockin1.settling_time_vg
=======
=======
>>>>>>> parent of 8aa3456 (major2)
box.settings.__setattr__("lockin3", empty())
box.settings.lockin3.address = "GPIB0::13"      # [string] address of lockin 3
box.settings.lockin3.reference = "external"
box.settings.lockin3.freq = box.settings.lockin1.freq  # [float] excitation current frequency (in Hz)
box.settings.lockin3.sampling_freq_plot = box.settings.lockin1.sampling_freq_plot
box.settings.lockin3.sampling_freq = box.settings.lockin1.sampling_freq
box.settings.lockin3.samples = box.settings.lockin1.samples
box.settings.lockin3.shield = "float"           # [string] shield ca nbe floating or shorted
box.settings.lockin3.coupling = "ac"            # [string] coupling can be ac or dc
box.settings.lockin3.time = 3                   # [float] integration time
box.settings.lockin3.filter = "24 dB/oct"       # [string] filter
box.settings.lockin3.input = "a-b"              # [string] input can be single ended or differential
box.settings.lockin3.sensitivity = "20 uV/pA"   # [string] sensitivity. The "/" is not a division symbols but stands for either Volts or Amperes.
box.settings.lockin3.harmonic = 1               # [int] demodulated harmonic
box.settings.lockin3.reserve = "normal"         # [string] reserve
box.settings.lockin3.settling_time_i = box.settings.lockin1.settling_time_i
box.settings.lockin3.settling_time_vb = box.settings.lockin1.settling_time_vb
box.settings.lockin3.settling_time_vg = box.settings.lockin1.settling_time_vg
<<<<<<< HEAD
>>>>>>> parent of 8aa3456 (major2)
=======
>>>>>>> parent of 8aa3456 (major2)
# ----- aiv settings -----
box.settings.__setattr__("aiv", empty())
box.settings.aiv.address = "ASRL2::INSTR"       # [string] address of aiv
box.settings.aiv.gain = 10e-3                   # [float] set the gain of the voltage controlled current amplifier
box.settings.aiv.isolation = "float"            # [string] isolation
box.settings.aiv.shield = "return"              # [string] shield
box.settings.aiv.compliance = 50                # [float] set the compliance to the highest level
box.settings.aiv.response = "fast"              # [string] set the response
# ----- avi settings -----
box.settings.__setattr__("avi", empty())
box.settings.avi.address = None
box.settings.avi.gain = 1e8                     # [float] set the gain of the voltage controlled current amplifier
# ----- smu settings -----
box.settings.__setattr__("sm", empty())
box.settings.smu.source = "v"
box.settings.smu.integration_time = 20e-3
box.settings.smu.samples = 0
box.settings.smu.sensing = "local"
box.settings.smu.address = "GPIB::1"           # [string] gate voltage source address
box.settings.smu.source_range = 110            # [float] gate voltage source range
box.settings.smu.sense_range = 100e-9          # [float] current sense range
box.settings.smu.compliance = 1e-6             # [float] voltage compliance
box.settings.smu.delay = 0.1                   # [float] time interval (in s) between source and measure (software controlled)
# endregion

# region ----- Read resources and create instrumentation objects -----
print("\n***** Loading instrumentation drivers *****")

rm = pyvisa.ResourceManager()

lockin1 = srs_sr830.sr830(visa=rm.open_resource(box.settings.lockin1.address))
print("Found lock-in 1: {}".format(lockin1.model))

lockin2 = srs_sr830.sr830(visa=rm.open_resource(box.settings.lockin2.address))
print("Found lock-in 2: {}".format(lockin2.model))

if mode == 1:
    lockin3 = srs_sr830.sr830(visa=rm.open_resource(box.settings.lockin3.address))
    print("Found lock-in 3: {}".format(lockin2.model))

aiv = srs_srcs580.srcs580(visa=rm.open_resource(box.settings.aiv.address))
print("Found I/V current amplifier: {}".format(aiv.model))

if box.settings.tc.model == 0:
    tc = lakeshore_tc336.tc336(visa=rm.open_resource(box.settings.tc.address))
    print("Found temperature controller: {}".format(tc.model))
elif box.settings.tc.model == 1:
    tc = oxford_mercury_itc.mercuryitc(box.settings.tc.address)
    print("Found temperature controller: {}".format(tc.model))
else:
    raise ValueError("Temperature controller ID does not belong to the list of the accepted values.")

aiv = srs_srcs580.srcs580(visa=rm.open_resource(box.settings.aiv.address))
print("Found I/V current amplifier: {}".format(aiv.model))

src = srs_srdc205.dc205(visa=rm.open_resource(box.settings.dc.address))
print("Found voltage source for device bias: {}".format(src.model))

smu = keithley_smu236.smu236(visa=rm.open_resource(box.settings.smu.address))
print("Found voltage source for device gate: {}".format(smu.model))

print("Done.")  # endregion

# region ----- Estimate measurement time and RAM -----
eta = (box.settings.tc.settling_time +
       box.settings.lockin1.settling_time * len(vg) * len(vb) +
       box.settings.lockin1.samples / box.settings.lockin1.sampling_freq) / 3600
ram = (len(t) * len(i) * len(vg) * len(vb) * 8 * (12 * 2 + 12 * box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)) / 1e6
# endregion

# region ----- Message to the user -----
print("\n"
      "***** Measurement summary *****\n"
      "chip: {}\n"
      "device: {}\n"
      "temperature : {} K\n"
      "heater: {}\n"
      "heater current : {} mA\n"
      "gate voltage: {} V\n"
      "bias voltage: {} V\n"
      "RAM required: {} MB\n"
      "No action is required from the USER during the measurement.\n"
      "Estimated measurement time: {:.1f} h.".
<<<<<<< HEAD
<<<<<<< HEAD
      format(box.chip, box.device, box.data.t, box.data.heater, box.data.i * 1000, box.data.vg, box.data.vb, ram, eta))
input("Press Enter to accept and proceed, press Ctrl-C to abort.")  # endregion

# region ----- Set or create current directory where to save files -----
print("\n***** Measurement log *****")
path = box.main + r"\\" + box.chip + "\\" + box.device + "\\"
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
lockin1.configure(box.settings.lockin1.reference, box.settings.lockin1.amplitude, box.settings.lockin1.freq,
                  box.settings.lockin1.harmonic, box.settings.lockin1.input, box.settings.lockin1.shield,
                  box.settings.lockin1.coupling, box.settings.lockin1.sensitivity, box.settings.lockin1.reserve,
                  box.settings.lockin1.time, box.settings.lockin1.filter, "both", box.settings.lockin1.sampling_freq,
                  "shot", "off")
lockin2.configure(box.settings.lockin2.reference, box.settings.lockin2.amplitude, box.settings.lockin2.freq,
                  box.settings.lockin2.harmonic, box.settings.lockin2.input, box.settings.lockin2.shield,
                  box.settings.lockin2.coupling, box.settings.lockin2.sensitivity, box.settings.lockin2.reserve,
                  box.settings.lockin2.time, box.settings.lockin2.filter, "both", box.settings.lockin2.sampling_freq,
                  "shot", "off")
if mode == 1:
    lockin3.configure(box.settings.lockin3.reference, box.settings.lockin3.amplitude, box.settings.lockin3.freq,
                      box.settings.lockin3.harmonic, box.settings.lockin3.input, box.settings.lockin3.shield,
                      box.settings.lockin3.coupling, box.settings.lockin3.sensitivity, box.settings.lockin3.reserve,
                      box.settings.lockin3.time, box.settings.lockin3.filter, "both", box.settings.lockin3.sampling_freq,
                      "shot", "off")
src.program_bias(0, box.settings.src.range, box.settings.src.isolation, box.settings.src.sensing)
smu.program_bias(box.settings.smu.source, 0, box.settings.smu.source_range, box.settings.smu.sense_range,
                 box.settings.smu.delay, box.settings.smu.samples, box.settings.smu.integration_time,
                 box.settings.smu.sensing, box.settings.smu.compliance)
aiv.configure(box.settings.aiv.gain, box.settings.aiv.response, box.settings.aiv.shield, box.settings.aiv.isolation,
              "on", "off", box.settings.aiv.compliance)
print("Done.")  # endregion

# region ----- Initialize figures -----
print("Initializing figure... ", end="")
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
plot0 = plot_stability_diagram(box.data)
plot1 = plot_te_stability_diagram(box.data)
plot2 = plot_obst(["stage", "shield"], box.settings.tc.settling_time)
plot3 = plot_obst(["x1", "y1", "x2", "y2", "x3", "y3"], box.settings.lockin1.settling_time)
plt.show(block=False)
plt.pause(.1)
print("Done.")  # endregion

# region ----- Allocate RAM -----
print("Allocating RAM... ", end="")
box.data = stability_diagram(heater, mode, t, i, vg, vb)
for idx_t, val_t in enumerate(box.data.t):
    box.data.tt[idx_t].time = zeros(int(ceil(box.settings.tc.settling_time * box.settings.tc.sampling_freq_plot)))
    box.data.tt[idx_t].temperature_stage = zeros(int(ceil(box.settings.tc.settling_time * box.settings.tc.sampling_freq_plot)))
    box.data.tt[idx_t].temperature_shield = zeros(int(ceil(box.settings.tc.settling_time * box.settings.tc.sampling_freq_plot)))

    for idx_i, val_i in enumerate(box.data.i):
        box.data.it[idx_t][idx_i].time = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
        box.data.it[idx_t][idx_i].x1 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
        box.data.it[idx_t][idx_i].y1 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
        box.data.it[idx_t][idx_i].x2 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
        box.data.it[idx_t][idx_i].y2 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
        if mode == 1:
            box.data.it[idx_t][idx_i].x3 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
            box.data.it[idx_t][idx_i].y3 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))

        for idx_vg, val_vg in enumerate(box.data.vg):
            for idx_vb, val_vb in enumerate(box.data.vb):
                box.data.vt[idx_t][idx_i][idx_vg][idx_vb].time = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x1 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y1 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x2 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y2 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                if mode == 1:
                    box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x3 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
                    box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y3 = zeros(int(ceil(box.settings.lockin1.settling_time * box.settings.lockin1.sampling_freq_plot)))
print("Done.")  # endregion

input("Unground the device, then press Enter to start measurement...")

for idx_t, val_t in enumerate(box.data.t):

    # region ----- Set temperature and wait for thermalization -----
    tc.set_temperature(output=0, setpoint=val_t)
    tc.set_temperature(output=1, setpoint=val_t) if box.settings.tc.model == 0 else None

    print("Waiting for thermalization at {:04.1f} K...".format(val_t), end="")
    box.data.tt[idx_t].setpoint = val_t

    k = 0
    t0 = time.time()
    plot2.ax.set_xlim([0, box.settings.tc.settling_time])
    plot2.ax.lines[3].set_data(x=array([0, box.settings.tc.settling_time]), y=array([val_t, val_t]))
    while time.time() - t0 <= box.settings.tc.settling_time:
        box.data.tt[idx_t].time[k] = time.time() - t0
        box.data.tt[idx_t].stage[k] = tc.read_temperature("a")
        box.data.tt[idx_t].shield[k] = tc.read_temperature("b")
        plot2.ax.lines[0].set_data(x=box.data.tt[idx_t].time[0:k+1], y=box.data.tt[idx_t].stage[0:k+1])
        plot2.ax.lines[1].set_data(x=box.data.tt[idx_t].time[0:k+1], y=box.data.tt[idx_t].shield[0:k+1])
        plt.pause(1 / box.settings.tc.sampling_freq_plot)
        k = k + 1
    plot2.fig.savefig(fname=box.filename + " - thermalization at {} K.png".format(val_t), format="png")
    print("Done.")  # endregion

    for idx_i, val_i in enumerate(box.data.i):

        # region ----- Set heater current ----------------------------------------
        print("Ramping up heater current to {:.1f} mA... ".format(box.data.i[idx_i] * 1000), end="")
        if box.data.i[idx_i] / box.settings.aiv.gain < 0.004:
            aiv.operation(input="off",
                          output="on")
        else:
            aiv.operation(input="on",
                          output="on")

        if idx_i == 0:
            i_ = 0
        else:
            i_ = box.data.i[idx_i - 1]

        lockin1.sweep_v(start=i_ / box.settings.aiv.gain / np.sqrt(2),
                        stop=val_i / box.settings.aiv.gain / np.sqrt(2),
                        n_step=int(floor(abs((val_i - i_)/box.settings.lockin1.step))),
                        rate=box.settings.lockin1.rate / box.settings.aiv.gain / np.sqrt(2))
        print("Done.")  # endregion

        # region ----- Set ac bias voltage ---------------------------------------
        print("Ramping up AC bias voltage from 0 V to {:.3f} V... ".format(box.settings.lockin2.amplitude), end="")
        lockin2.sweep_v(start=0,
                        stop=box.settings.lockin2.amplitude / np.sqrt(2),
                        n_step=int(floor((box.settings.lockin2.amplitude-0)/box.settings.lockin2.step)),
                        rate=box.settings.lockin2.rate / np.sqrt(2))
        print("Done.")  # endregion

        # region ----- Wait for steady state -------------------------------------
        t0 = time.time()
        idx = 0
        print("Waiting for steady state... ", end="")
        while time.time() - t0 <= box.settings.lockin1.settling_time_i:

            box.data.it[idx_t][idx_i].time[idx] = time.time() - t0
            box.data.it[idx_t][idx_i].x1[idx], box.data.it[idx_t][idx_i].y1[idx] = lockin1.read() * np.sqrt(2)
            box.data.it[idx_t][idx_i].x2[idx], box.data.it[idx_t][idx_i].y2[idx] = lockin2.read() * np.sqrt(2)
            if mode == 1:
                box.data.it[idx_t][idx_i].x3[idx], box.data.it[idx_t][idx_i].y3[idx] = lockin3.read() * np.sqrt(2)

            plot3.ax.lines[0].set_data(x=box.data.it[idx_t][idx_i].time[0:idx+1], y=box.data.it[idx_t][idx_i].x1[0:idx+1])
            plot3.ax.lines[1].set_data(x=box.data.it[idx_t][idx_i].time[0:idx+1], y=box.data.it[idx_t][idx_i].y1[0:idx+1])
            plot3.ax.lines[2].set_data(x=box.data.it[idx_t][idx_i].time[0:idx+1], y=box.data.it[idx_t][idx_i].x2[0:idx+1])
            plot3.ax.lines[3].set_data(x=box.data.it[idx_t][idx_i].time[0:idx+1], y=box.data.it[idx_t][idx_i].y2[0:idx+1])
            if mode == 1:
                plot3.ax.lines[4].set_data(x=box.data.it[idx_t][idx_i].time[0:idx+1], y=box.data.it[idx_t][idx_i].x3[0:idx+1])
                plot3.ax.lines[5].set_data(x=box.data.it[idx_t][idx_i].time[0:idx+1], y=box.data.it[idx_t][idx_i].y3[0:idx+1])

            plt.pause(0.001)
            idx = idx + 1

        plot2.fig.savefig(fname=box.filename + " - thermalization at {} K and {:.4f} A.png".format(val_t, val_i), format="png")
        print("Done.")  # endregion

        for idx_vg, val_vg in enumerate(box.data.vg):

            # region ----- Set gate voltage -----
            if idx_vg == 0:
                vg_ = 0
            else:
                vg_ = box.data.vg[idx_vg - 1]

            print("Sweeping gate voltage from {} V to {} V... ".format(vg_, val_vg), end="")
            smu.sweep_bias(source=box.settings.smu.source,
                           start=vg_,
                           stop=val_vg,
                           n_step=int(np.floor(val_vg-vg_ / 10e-3)),
                           rate=10e-3,
                           source_range=box.settings.smu.source_range,
                           sense_range=box.settings.smu.sense_range,
                           compliance=box.settings.smu.compliance)
            print("Done.")  # endregion

            # region ----- Wait for steady state -----
            print("Waiting for steady state... ", end="")
            t0 = time.time()
            while time.time() - t0 <= box.settings.lockin1.settling_time_vg:
                plt.pause(0.001)
            print("Done.")  # endregion

            for idx_vb, val_vb in enumerate(box.data.vb):

                # region ----- Sweep bias voltage -----
                if idx_vg == 0:
                    vb_ = 0
                else:
                    vb_ = box.data.vb[idx_vb - 1]
                print("Sweeping bias voltage from {} V to {} V... ".format(vb_, val_vb), end="")

                print("Done.")  # endregion

                # region ----- Wait for steady state -----
                print("Waiting for steady state... ", end="")
                idx = 0
                t0 = time.time()
                while time.time() - t0 <= box.settings.lockin1.settling_time_vb:

                    box.data.vt[idx_t][idx_i][idx_vg][idx_vb].time[idx] = time.time() - t0
                    box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x1[idx], box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y1[idx] = lockin1.read() * np.sqrt(2)
                    box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x2[idx], box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y2[idx] = lockin2.read() * np.sqrt(2)
                    if mode == 1:
                        box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x3[idx], box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y3[idx] = lockin3.read() * np.sqrt(2)

                    plot3.ax.lines[0].set_data(x=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].time[0:idx+1], y=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x1[0:idx+1])
                    plot3.ax.lines[1].set_data(x=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].time[0:idx+1], y=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y1[0:idx+1])
                    plot3.ax.lines[2].set_data(x=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].time[0:idx+1], y=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x2[0:idx+1])
                    plot3.ax.lines[3].set_data(x=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].time[0:idx+1], y=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y2[0:idx+1])
                    if mode == 1:
                        plot3.ax.lines[4].set_data(x=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].time[0:idx+1], y=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].x3[0:idx+1])
                        plot3.ax.lines[5].set_data(x=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].time[0:idx+1], y=box.data.vt[idx_t][idx_i][idx_vg][idx_vb].y3[0:idx+1])

                    plt.pause(0.001)
                    idx = idx + 1
                print("Done.")  # endregion

                # region ----- Measure -----
                print("Temperature: {} K. Heater current: {} A. Gate: {} V. Bias: {} V. Measuring... ".format(t, i, vg, vb), end="")

                # start measurement in hardware and release CPU
                lockin1.start_filling_buffer()
                lockin2.start_filling_buffer()
                if mode == 1:
                    lockin3.start_filling_buffer()

                # wait for buffer full
                lockin1.wait_for_buffer_full(box.settings.lockin1.samples)
                lockin2.wait_for_buffer_full(box.settings.lockin2.samples)
                if mode == 1:
                    lockin3.wait_for_buffer_full(box.settings.lockin3.samples)

                # read lockins buffer
                x1 = lockin1.read_buffer(1, 0, box.settings.lockin1.samples, "binary")
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 0] = np.mean(x1) / box.settings.avi.gain
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 1] = np.std(x1) / box.settings.avi.gain

                y1 = lockin1.read_buffer(2, 0, box.settings.lockin1.samples, "binary")
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 2] = np.mean(y1) / box.settings.avi.gain
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 3] = np.std(y1) / box.settings.avi.gain

                x2 = lockin2.read_buffer(1, 0, box.settings.lockin2.samples, "binary")
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 4] = np.mean(x2) / box.settings.avi.gain
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 5] = np.std(x2) / box.settings.avi.gain

                y2 = lockin2.read_buffer(2, 0, box.settings.lockin2.samples, "binary")
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 6] = np.mean(y2) / box.settings.avi.gain
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 7] = np.std(y2) / box.settings.avi.gain

                if mode == 1:
                    x3 = lockin3.read_buffer(1, 0, box.settings.lockin3.samples, "binary")
                    box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 8] = np.mean(x3)
                    box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 9] = np.std(x3)

                    y3 = lockin3.read_buffer(2, 0, box.settings.lockin3.samples, "binary")
                    box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 10] = np.mean(y3)
                    box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 11] = np.std(y3)

                # read gate leakage current
                v_gate, i_gate = smu.read()
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 12] = v_gate
                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 14] = i_gate

                box.data.sd[idx_t][idx_i][idx_vg, idx_vb, 13] = val_vb
                print("done")  # endregion

                # region ----- Update figures -----
                # update "data vs gate"
                plot0.ax01.lines[idx_vb].set_data(x=box.data.vg[0:idx_vg+1], y=box.data.sd[idx_t][idx_i][0:idx_vg+1, idx_vb, 4])
                plot0.ax11.lines[idx_vb].set_data(x=box.data.vg[0:idx_vg+1], y=abs(box.data.sd[idx_t][idx_i][0:idx_vg+1, idx_vb, 4]))
                plot1.ax01.lines[idx_vb].set_data(x=box.data.vg[0:idx_vg+1], y=box.data.sd[idx_t][idx_i][0:idx_vg+1, idx_vb, 2])
                plot1.ax11.lines[idx_vb].set_data(x=box.data.vg[0:idx_vg+1], y=abs(box.data.sd[idx_t][idx_i][0:idx_vg+1, idx_vb, 2]))

                # update "data vs vb"
                plot0.ax00.lines[idx_vg].set_data(x=box.data.vb[0:idx_vb+1], y=box.data.sd[idx_t][idx_i][idx_vg, 0:idx_vb+1, 4])
                plot0.ax10.lines[idx_vg].set_data(x=box.data.vb[0:idx_vb+1], y=abs(box.data.sd[idx_t][idx_i][idx_vg, 0:idx_vb+1, 4]))
                plot1.ax00.lines[idx_vg].set_data(x=box.data.vb[0:idx_vb+1], y=box.data.sd[idx_t][idx_i][idx_vg, 0:idx_vb+1, 2])
                plot1.ax10.lines[idx_vg].set_data(x=box.data.vb[0:idx_vb+1], y=abs(box.data.sd[idx_t][idx_i][idx_vg, 0:idx_vb+1, 2]))

                # update "stability diagrams"
                plot0.ax02.images[0].set_data(box.data.sd[idx_t][idx_i][0:idx_vg+1, 0:idx_vb+1, 4])
                plot0.ax02.relim()
                plot0.ax12.images[0].set_data(abs(box.data.sd[idx_t][idx_i][0:idx_vg+1, 0:idx_vb+1, 4]))
                plot0.ax12.relim()
                plot1.ax02.images[0].set_data(box.data.sd[idx_t][idx_i][0:idx_vg+1, 0:idx_vb+1, 2])
                plot1.ax02.relim()
                plot1.ax12.images[0].set_data(abs(box.data.sd[idx_t][idx_i][0:idx_vg+1, 0:idx_vb+1, 2]))
                plot1.ax12.relim()
                plt.pause(0.001)  # endregion

            # region ----- Save data and figure to disc -----
            if os.path.exists(box.filename):
                if os.path.exists(box.backupname):
                    os.remove(box.backupname)
                os.rename(box.filename, box.backupname)
            with open(box.filename, "wb") as file:
                pickle.dump(box, file)
            plot0.fig.savefig(fname=box.filename + " - stability diagram - {}.png", format="png")
            plot1.fig.savefig(fname=box.filename + " - thermoelectric stability diagram.png", format="png")
            # endregion

# region ----- Ramping down to zero all sources and terminate program-----
<<<<<<< HEAD
<<<<<<< HEAD
print("Ramping down heater current from {:.1f} mA to 0 V... ".format(val_i), end="")
lockin1.sweep_v(start=val_i / box.settings.aiv.gain / np.sqrt(2),
                stop=0,
                n_step=100,
                rate=10e-6 / box.settings.aiv.gain / np.sqrt(2))
=======
=======
>>>>>>> parent of 8aa3456 (major2)
print("Ramping down heater current from {:.1f} mA to 0 V... ".format(i), end="")
lockin1.sweep_v(
    start=val_i / box.settings.aiv.gain / np.sqrt(2),
    stop=0,
    n_step=100,
    rate=10e-6 / box.settings.aiv.gain / np.sqrt(2)
)
>>>>>>> parent of 8aa3456 (major2)
print("Done.")

print("Ramping down AC bias voltage from {:.1f} V to 0 V... ".format(box.settings.lockin2.amplitude), end="")
lockin2.sweep_v(start=box.settings.lockin2.amplitude,
                stop=0,
                n_step=100,
                rate=1e-3 / np.sqrt(2))
print("Done.")

<<<<<<< HEAD
<<<<<<< HEAD
print("Ramping down DC bias voltage from {} V to 0 V... ".format(val_vb), end="")
src.sweep_voltage(start=val_vb,
                  stop=0,
                  nstep=int(np.floor(val_vb / box.settings.src.step)),
                  rate=box.settings.src.rate)
print("Done.")

print("Ramping down gate voltage from {} V to 0 V... ".format(val_vg), end="")
smu.sweep_bias(source=box.settings.smu.source,
               start=val_vg,
               stop=0,
               n_step=int(np.floor(val_vg / 10e-3)),
               rate=10e-3,
               source_range=box.settings.smu.source_range,
               sense_range=box.settings.smu.sense_range,
               compliance=box.settings.smu.compliance)
=======
=======
>>>>>>> parent of 8aa3456 (major2)
print("Ramping down DC bias voltage from {} V to 0 V... ".format(vb), end="")
src.sweep_voltage(
    start=val_vb,
    stop=0,
    nstep=int(np.floor(val_vb / 1e-3)),
    rate=10e-3
)
print("Done.")

print("Ramping down gate voltage from {} V to 0 V... ".format(vg), end="")
smu.sweep_bias(
    source=box.settings.smu.source,
    start=val_vg,
    stop=0,
    n_step=int(np.floor(val_vg / 10e-3)),
    rate=10e-3,
    source_range=box.settings.smu.source_range,
    sense_range=box.settings.smu.sense_range,
    compliance=box.settings.smu.compliance)
>>>>>>> parent of 8aa3456 (major2)
print("Done.")

os.remove(box.backupname)
plt.show()  # endregion

