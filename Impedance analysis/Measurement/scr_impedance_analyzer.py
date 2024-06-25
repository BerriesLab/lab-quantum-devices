from agilent_4294a import *
from datetime import date
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.gridspec as gs
import pyvisa as visa
import pickle
import datetime
import time

# region ----- USER inputs -----
# measurement(s) options -----------------------------------------------------------------------------------------------
main = r"C:\samples\dabe"            # [string] Main folder directory
chip = "qd_gr_00"                         # [string] chip name
device = "je"                       # [string] device name
material = ""               # [string] material
environment = "vacuum"                     # [string] measurement environment
illumination = "dark"
temperature = 21
comments = ""
imp_analyzer_address = "GPIB0::17::INSTR"
# impedance anylsis options --------------------------------------------------------------------------------------------
dc_bias = [-1, 1, 0.2]        # start, stop, step
#dc_bias = [0, 0, 1]            # set to 0 for open/short compensation
measure = 'IMPH' # measure impedance and phase
mode = 'VOLT'
level = 0.01   # oscillator level
bandwidth = 5
average = 'OFF'
point_averaging = 16
s_param = 'FREQ'
s_type = 'LOG'
s_start = 40
s_stop = 1e6
s_points = 201
s_point_delay = 0.1
s_sweep_delay = 10
# endregion USER input

# region ----- Set or create current directory where to save files -----
print("\n***** Measurement log *****")
path = main + "/" + chip + "/" + device + "/impedance analysis/"
try:
    os.chdir(path)  # if path exists, then make it cwd
    print("{} ... found.".format(path))
except OSError:  # if path does not exists
    print("{} ... not found. Making directory... ".format(path), end="")
    os.makedirs(path)  # make new directory
    os.chdir(path)  # make path cwd
    print("Done.")
print("Current working directory set to: {}".format(os.getcwd()))
print("Done.")
# endregion

# region ----- Read resources and create instrumentation objects -----
print("Listing instrumentation... ")
rm = visa.ResourceManager()
try:
    # define impedance anylsis object
    imp = rm.open_resource(imp_analyzer_address)
    print("Found impedance anaylzer: {}".format(imp.query("*IDN?")))
except visa.VisaIOError as e:
    exit("Cannot find impedance anaylzer... Execution terminated.")
# endregion

# initialize measuring tools
imp.timeout = 5000000                 # increase if pyvisa timeout during impedance anaylzer sweep
impedance_analyzer = agilent4294a(visa=imp)
impedance_analyzer.set_measurement_parameters(meas=measure)
impedance_analyzer.set_measurement_signals(mode=mode, level=level)
impedance_analyzer.set_averaging(bandwidth=bandwidth, point_averaging=point_averaging, average=average)
impedance_analyzer.set_sweep_condition(parameter=s_param, type=s_type, start=s_start, stop=s_stop, points=s_points, point_delay=s_point_delay, sweep_delay=s_sweep_delay)  # max 801 points

# fixture compensation (comment when done)
# note: compensation data can be read
#ans = input("Proceed with ficture compensation? [y/n]")
#if ans == "y":
#    impedance_analyzer.fixture_compensation()

# create dc bias array
bias = np.linspace(dc_bias[0], dc_bias[1], int((dc_bias[1] - dc_bias[0]) / dc_bias[2] + 1))
#bias = np.array([-10, -9, -8, 0, 8, 9, 10])
# dcbias = np.linspace(start=vstart, stop=vstop, num=vnum, endpoint=True)

p_averaging = point_averaging if average == 'ON' else 1
time_bandwidth = {1: 0.005, 20: 0.009, 3: 0.04, 4: 0.08, 5: 0.2} # rough estimate
time_per_point = s_point_delay + p_averaging * time_bandwidth[bandwidth]
total_time = len(bias) * (s_sweep_delay + s_points * time_per_point)
print("Estimated measurement time > ~" + str(np.rint(total_time/60)) + " min.")
input("Press Enter to accept and proceed, press Ctrl-C to abort.")

# create color scale for plotting
# cm = cm.RdYlBu_r
cm = matplotlib.cm.get_cmap("coolwarm")
norm = matplotlib.colors.Normalize(vmin=bias.min(), vmax=bias.max())

# create figures
fig = plt.figure(figsize=(40 / 2.54, 25 / 2.54))
gs = gs.GridSpec(2, 1)
#gs = gs.GridSpec(3, 2)
ax1 = fig.add_subplot(gs[0, :])
ax2 = fig.add_subplot(gs[1, :])
#ax3 = fig.add_subplot(gs[2, 0])
#ax4 = fig.add_subplot(gs[2, 1])

ax1.set_xlabel('Frequency [Hz]')
ax1.set_ylabel('Impedance modulus [Ohm]')

ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Impedance phase [°]')  # we already handled the x-label with ax1

#ax3.set_xlabel('Real')
#ax3.set_ylabel('Imaginary')

#ax4.set_xlabel('Frequency [Hz]')
#ax4.set_ylabel('Magnitude')

plt.show(block=False)

start_count = time.time()
for idx, val in enumerate(bias):
    impedance_analyzer.set_onscreen_arrangement()

    # set bias voltage
    # if val < 1:
    print(f"Setting DC bias to {val:.2f} V. ", end="")
    impedance_analyzer.set_dc_bias(mode='VOLT', level=val, range=1e-3)
    # else:
    #    impedance_analyzer.set_dc_bias(mode='VOLT', level=val, range=100e-3)

    impedance_analyzer.switch_dc_bias(state='ON')

    # acquire impedance spectra for each bias voltage
    print("Measuring... ", end="")
    f, r, p = impedance_analyzer.sweep_and_acquire()
    elapsed_time = (time.time() - start_count)
    print("Done. Elapsed time: {}.".format(time.strftime("%H.%M.%S", time.gmtime(elapsed_time))))

    # turn off bias voltage
    impedance_analyzer.switch_dc_bias(state='OFF')

    # read impedance analyzer settings
    settings = impedance_analyzer.read_settings()

    # Save impedance spectra

    # Save data
    date = datetime.datetime.now()
    file_name = "{} - frequency sweep - bias {}V - {} - {} - {}C.bin".format(date.strftime("%Y.%m.%d %H.%M.%S"), val,
                                                                             environment,
                                                                             illumination,
                                                                             temperature)

    with open(file_name, "wb") as file:
        pickle.dump({"date": date,
                     "chip": chip,
                     "device": device,
                     "bias": val,
                     "datetime": date,
                     "environment": environment,
                     "illumination": illumination,
                     "comments": comments,
                     "material": material,
                     "temperature": temperature,
                     "data": {"frequency": f,
                              "impedance_modulus": r,
                              "impedance_phase": p},
                     "settings": {"impedance_analyzer": impedance_analyzer.read_settings()}}, file)

    txt_data = np.array([f, r, p]).T
    # txt_settings = str(impedance_analyzer.read_settings())
    np.savetxt(file_name[:-3] + "txt", txt_data, delimiter=",", newline='\n',
               header="frequency,impedance_modulus,impedance_phase",
               comments="", footer='', encoding=None)

    # calculate real and imaginary
    x = r * np.cos(p * np.pi / 180)
    y = r * np.sin(p * np.pi / 180)

    # plot data
    ax1.loglog(f, r, color=cm(norm(val)), alpha=0.4, linewidth=0, marker='o', label=f"{val:.2f}")
    ax1.legend(loc="upper right", title='DC bias voltage')
    ax2.semilogx(f, p, color=cm(norm(val)), alpha=0.4, linewidth=0, marker='o')
    #ax3.plot(x, abs(y), color=cm(norm(val)), alpha=0.4, linewidth=0, marker='o')
    #ax4.semilogx(f, x, color=cm(norm(val)), alpha=0.4, linewidth=0, marker='o')
    #ax4.semilogx(f, abs(y), color=cm(norm(val)), alpha=0.4, linewidth=0, marker='*')
    plt.savefig(fname=file_name[:-3] + "png", format="png")
    plt.pause(0.01)

# fig.tight_layout()  # otherwise the right y-label is slightly clipped
print("Measurement completed.")

plt.show()
