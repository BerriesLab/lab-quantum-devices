import numpy as np
import time
import struct
from collections import defaultdict


class sr830():

    ''' Communications with the SR830 uses ASCII characters. Commands may be in either UPPER or lower case and may contain any number of
embedded space characters. A command to the SR830 consists of a four character command mnemonic, arguments if necessary, and a command terminator.
The terminator must be a linefeed <lf> or carriage return <cr> on RS232, or a linefeed <lf> or EOI on GPIB. No command processing occurs until a
command terminator is received. Commands function identically on GPIB and RS232 whenever possible. Command mnemonics beginning with an
asterisk "❊" are IEEE488.2 (1987) defined common commands. These commands also function identically on RS232. Commands may require one
or more parameters. Multiple parameters are separated by commas (,). Multiple commands may be sent on one command line by separating them
with semicolons (;). The difference between sending several commands on the same line and sending several independent commands is that
when a command line is parsed and executed, the entire line is executed before any other device action proceeds. There is no need to
wait between commands. The SR830 has a 256 character input buffer and processes commands in the order received. If the buffer fills up,
the SR830 will hold off handshaking on the GPIB and attempt to hold off handshaking on RS232. Similarly, the SR830 has a 256
character output buffer to store outputs until the host computer is ready to receive. If either buffer overflows,
both buffers are cleared and an error reported. '''

    # SCPI dictionary for writing to instrumentation (refer to manual)
    scpi_w = {"fmod": {"internal": "1",
                       "external": "0"},
              "isrc": {"a": "0",
                       "a-b": "1",
                       "i (1 MOhm)": "2",
                       "i (100 MOhm)": "3"},
              "ignd": {"float": "0",
                       "ground": "1"},
              "icpl": {"ac": "0",
                       "dc": "1"},
              "ilin": {"no filter": "0",
                       "line": "1",
                       "2x line": "2",
                       "both": "3"},
              "sens": {2e-9: "0",
                       5e-9: "1",
                       10e-9: "2",
                       20e-9: "3",
                       50e-9: "4",
                       100e-9: "5",
                       200e-9: "6",
                       500e-9: "7",
                       1e-6: "8",
                       2e-6: "9",
                       5e-6: "10",
                       10e-6: "11",
                       20e-6: "12",
                       50e-6: "13",
                       100e-6: "14",
                       200e-6: "15",
                       500e-6: "16",
                       1e-3: "17",
                       2e-3: "18",
                       5e-3: "19",
                       10e-3: "20",
                       20e-3: "21",
                       50e-3: "22",
                       100e-3: "23",
                       200e-3: "24",
                       500e-3: "25",
                       1: "26"},
              "rmod": {"high reserve": "0",
                       "normal": "1",
                       "low noise": "2"},
              "oflt": {10E-6: "0",
                       30E-6: "1",
                       100E-6: "2",
                       300E-6: "3",
                       1E-3: "4",
                       3E-3: "5",
                       10E-3: "6",
                       30E-3: "7",
                       100E-3: "8",
                       300E-3: "9",
                       1: "10",
                       3: "11",
                       10: "12",
                       30: "13",
                       100: "14",
                       300: "15",
                       1E3: "16",
                       3E3: "17",
                       10E3: "18",
                       30E3: "19"},
              "ofsl": {"6 dB/oct": "0",
                       "12 dB/oct": "1",
                       "18 dB/oct": "2",
                       "24 dB/oct": "3"},
              "srat": {62.5E-3: "0",
                       125E-3: "1",
                       250E-3: "2",
                       500E-3: "3",
                       1: "4",
                       2: "5",
                       4: "6",
                       8: "7",
                       16: "8",
                       32: "9",
                       64: "10",
                       128: "11",
                       256: "12",
                       512: "13",
                       "trigger": "14"},
              "send": {"shot": "1",
                       "loop": "0"},
              "outx": {"rs232": "0",
                       "gpib": "1"},
              "sync": {"off": "0",
                       "on": "1"},
              "tran": {"off": 0,
                       "on dos": 1,
                       "on win": 2}}

    # SCPI dictionary for reading from instrumentation
    scpi_r = defaultdict(dict)
    for key, val in scpi_w.items():
        for subkey, subval in val.items():
            scpi_r[key][subval] = subkey

    def __init__(self, visa, wait=0.01):
        # create an empty local registry and populate the registry with the current instrumentation settings
        # when adding/removing parameters, amend "get_settings" method

        self.visa = visa
        self.wait = wait  # Wait time (in s) after each read / write operation
        self.model = self.read_model()
        self.visa.write("*RST")  # restore unit to factory default
        self.set_interface("gpib")
        self.set_amplitude(0)


    '''----- Set settings functions -----'''

    def set_reference(self, reference):
        # set reference
        self.visa.write("FMOD {}".format(self.scpi_w["fmod"][reference]))
        time.sleep(self.wait)

    def set_frequency(self, frequency):
        # set frequency
        self.visa.write("FREQ {}".format(frequency))
        time.sleep(self.wait)

    def set_harmonic(self, harmonic):
        # set harmonic
        self.visa.write("HARM {}".format(harmonic))
        time.sleep(self.wait)

    def set_input(self, input):
        # set input
        self.visa.write("ISRC {}".format(self.scpi_w["isrc"][input]))
        time.sleep(self.wait)

    def set_shield(self, shield):
        # set shield
        self.visa.write("IGND {}".format(self.scpi_w["ignd"][shield]))
        time.sleep(self.wait)

    def set_coupling(self, coupling):
        # set coupling
        self.visa.write("ICPL {}".format(self.scpi_w["icpl"][coupling]))
        time.sleep(self.wait)

    def set_notch(self, notch):
        # set notch
        self.visa.write("ILIN {}".format(self.scpi_w["ilin"][notch]))
        time.sleep(self.wait)

    def set_sensitivity(self, sensitivity):
        # set sensitivity
        self.visa.write("SENS {}".format(self.scpi_w["sens"][sensitivity]))
        time.sleep(self.wait)

    def set_reserve(self, reserve):
        # set reserve
        self.visa.write("RMOD {}".format(self.scpi_w["rmod"][reserve]))
        time.sleep(self.wait)

    def set_integration_time(self, integration_time):
        # set integration time
        self.visa.write("OFLT {}".format(self.scpi_w["oflt"][integration_time]))
        time.sleep(self.wait)

    def set_filter(self, filter):
        # set filter
        self.visa.write("OFSL {}".format(self.scpi_w["ofsl"][filter]))
        time.sleep(self.wait)

    def set_sync_filter(self, sync):
        # set synchronous filter
        self.visa.write("SYNC {}".format(self.scpi_w["sync"][sync]))
        time.sleep(self.wait)

    def set_interface(self, interface):
        # set communication interface
        self.visa.write("OUTX {}".format(self.scpi_w["outx"][interface]))
        time.sleep(self.wait)

    def set_sampling_frequency(self, frequency):
        # set sampling frequency
        self.visa.write("SRAT {}".format(self.scpi_w["srat"][frequency]))
        time.sleep(self.wait)

    def set_buffer_type(self, buffer):
        # When the buffer becomes full, data storage can stop or continue. The first case is called 1 Shot (data points are stored for a single buffer length).
        # At the end of the buffer, data storage stops and an audio alarm sounds. The second case is called Loop. In this case, data storage continues at
        # the end of the buffer. The data buffer will store 16383 points and start storing at the beginning again. The most recent 16383 points will be
        # contained in the buffer. Once the buffer has looped around, the oldest point (at any time) is at bin#0 and the most recent point is at bin
        self.visa.write("SEND {}".format(self.scpi_w["send"][buffer]))
        time.sleep(self.wait)

    def set_amplitude(self, amplitude):
        # The "SLVL x" command sets or queries the amplitude of the sine output.
        # The parameter x is a voltage (real number of Volts). The value of x will
        # be rounded to 0.002V. The value of x is limited to 0.004 <= x <= 5.000.
        if amplitude <= 0.004:
            self.visa.write("SLVL 0.004")
        else:
            self.visa.write("SLVL {}".format(amplitude))
        time.sleep(self.wait)

    def set_data_transfer_mode(self, mode="off"):
        # data transfer mode can be slow ("off") fast for windows ("on win") or fast for dos ("on dos")
        # when fast, data is transmitted in binary format
        # The values of X and Y are transferred as signed integers, 2 bytes long (16 bits). X is
        # sent first followed by Y for a total of 4 bytes per sample. The values range from -32768
        # to 32767. The value ±30000 represents ±full scale (i.e. the sensitivity).
        #  Offsets and expands are included in the values of X and Y. The transferred values are
        # (raw data - offset) x expand. The resulting value must still be a 16 bit integer. The value
        # ±30000 now represents ±full scale divided by the expand factor.
        # The transfer mode should be turned on (using FAST1 or FAST 2) before a scan is
        # started. Then use the STRD command (see below) to start a scan. After sending the
        # STRD command, immediately make the SR830 a talker and the controlling interface a
        # listener. Remember, the first transfer will occur with the first point in the scan. If the
        # scan is started from the front panel or from a trigger, then make sure that the SR830 is
        # a talker and the controlling interface a listener BEFORE the scan actually starts.
        self.visa.write("fast {}".format(self.scpi_w["tran"][mode]))
        time.sleep(self.wait)

    '''----- Read settings functions -----'''

    def read_reference(self):
        # read reference
        val = self.scpi_r["fmod"][self.visa.query("FMOD?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_frequency(self):
        # read frequency
        val = self.visa.query("FREQ?").strip("\n")
        time.sleep(self.wait)
        return val

    def read_harmonic(self):
        # read harmonic
        val = self.visa.query("HARM?").strip("\n")
        time.sleep(self.wait)
        return val

    def read_input(self):
        # read input
        val = self.scpi_r["isrc"][self.visa.query("ISRC?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_shield(self):
        # read shield
        val = self.scpi_r["ignd"][self.visa.query("IGND?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_coupling(self):
        # read coupling
        val = self.scpi_r["icpl"][self.visa.query("ICPL?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_notch(self):
        # read notch
        val = self.scpi_r["ilin"][self.visa.query("ILIN?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_sensitivity(self):
        # read sensitivity
        val = self.scpi_r["sens"][self.visa.query("SENS?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_reserve(self):
        # read reserve
        val = self.scpi_r["rmod"][self.visa.query("RMOD?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_integration_time(self):
        # read integration time
        val = self.scpi_r["oflt"][self.visa.query("OFLT?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_filter(self):
        # read filter
        val = self.scpi_r["ofsl"][self.visa.query("OFSL?").strip("\n").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_sync_filter(self):
        # read synchronous filter
        val = self.scpi_r["sync"][self.visa.query("SYNC?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_interface(self):
        # read communication interface
        val = self.scpi_r["outx"][self.visa.query("OUTX?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_sampling_frequency(self):
        # read sampling frequency
        val = self.scpi_r["srat"][self.visa.query("SRAT?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_buffer_type(self):
        # read buffer type
        val = self.scpi_r["send"][self.visa.query("SEND?").strip("\n")]
        time.sleep(self.wait)
        return val

    def read_model(self):
        # return model number
        val = self.visa.query("*IDN?").strip("\n")
        time.sleep(self.wait)
        return val

    def read_data_transfer_mode(self):
        val = self.scpi_r["tran"][self.visa.query("fast?").strip("\n")]
        time.sleep(self.wait)
        return val

    '''----- Operation functions -----'''

    def sweep_v(self, start, stop, n_step=1000, rate=0.01):
        # run through all the output voltage values
        if start != stop:
            if (abs((stop - start) / n_step) + 1) / rate > self.wait:
                delay = abs((stop - start) / n_step) / rate
            else:
                delay = self.wait
            for v in np.linspace(start, stop, n_step, endpoint=True):
                # Set the voltage output value to 0.004 if  v <= 0.004V, otherwise set the voltage output to v
                self.set_amplitude(v)
                time.sleep(delay)

    def read(self):
        xy = self.visa.query("SNAP? 1, 2, 9")
        time.sleep(self.wait)
        x = np.single(xy.split(",")[0])
        y = np.single(xy.split(",")[1])
        # freq = np.single(xy.split(",")[2])
        return x, y

    def read_buffer(self, channel, bin_start=0, bin_end=16383, mode="ascii"):
        # read buffer in mode "mode". Bins are numbered from 0 to N-1, where N is the number of samples stored in buffer
        self.pause_buffer()
        if mode == "ascii":
            reading = self.visa.query("TRCA?{},{},{}".format(channel, bin_start, bin_end)).split(",")[0:-1]
            reading = np.array([float(x) for x in reading])
        elif mode == "binary":
            self.visa.write("TRCB?{},{},{}".format(channel, bin_start, bin_end))
            reading = self.visa.read_raw()
            reading = np.array([float(x[0]) for x in struct.iter_unpack('f', reading)])
        time.sleep(self.wait)
        return reading

    def start_filling_buffer(self):
        self.reset_buffer()
        self.visa.write("STRT")
        time.sleep(self.wait)

    def pause_buffer(self):
        # reset buffer
        self.visa.write("PAUS")
        time.sleep(self.wait)

    def reset_buffer(self):
        # stop buffer storage and reset buffer
        self.visa.write("REST")
        time.sleep(self.wait)

    def send_trigger(self):
        self.visa.write("TRIG")  # send a trigger signal to the lockin
        time.sleep(self.wait)

    def stop(self):
        self.visa.write("SLVL 0.004")
        time.sleep(self.wait)

    def configure(self, reference="internal", amplitude=0, frequency=1000, harmonic=1, input="a-b", shield="float", coupling="ac", sensitivity="20 uV/pA",
                reserve="normal", integration_time=100e-3, filter="24 dB/oct", notch="no filter", sampling=512, buffer="shot", sync="off"):
        # the unit is always on. To start storing readings in the buffer one has to run "measure"
        self.set_reference(reference)
        if reference == "internal":
            self.set_frequency(frequency)
            self.set_amplitude(amplitude)
        self.set_harmonic(harmonic)
        self.set_amplitude(amplitude)
        self.set_input(input)
        self.set_shield(shield)
        self.set_coupling(coupling)
        self.set_sensitivity(sensitivity)
        self.set_reserve(reserve)
        self.set_integration_time(integration_time)
        self.set_filter(filter)
        self.set_notch(notch)
        self.set_sampling_frequency(sampling)
        self.set_buffer_type(buffer)
        self.set_sync_filter(sync)
        self.reset_buffer()

    def measure(self, samples, reference="internal", frequency=1000, harmonic=1, input="a", shield="float", coupling="ac", sensitivity="1 V/uA",
                reserve="normal", time=1E-3, filter="6 dB/oct", notch="both", sampling=512, buffer="shot", sync="off"):
        self.configure(reference, frequency, harmonic, input, shield, coupling, sensitivity, reserve, time,
                             filter, notch, sampling, buffer, sync)
        self.start_filling_buffer()
        self.wait_for_buffer_full(size=samples)
        data1 = self.read_buffer(channel=1, bin_start=0, bin_end=samples)
        data2 = self.read_buffer(channel=2, bin_start=0, bin_end=samples)
        return data1, data2

    def wait_for_buffer_full(self, size):
        # sr830 cannot raise a service request when the buffer is full. One should query the buffer size and wait until full
        while int(self.visa.query("SPTS?").strip("\n")) < size:
            time.sleep(self.wait)
            continue

    def get_settings(self):
        # read local registry and return a list of tuples (dictionary)
        return {"unit": self.read_model(),
                "frequency": self.read_frequency(),
                "reference": self.read_reference(),
                "harmonic": self.read_harmonic(),
                "input": self.read_input(),
                "shield": self.read_shield(),
                "coupling": self.read_coupling(),
                "sensitivity": self.read_sensitivity(),
                "reserve": self.read_reserve(),
                "integration time": self.read_integration_time(),
                "filter": self.read_filter(),
                "notch filter": self.read_notch(),
                "sampling frequency": self.read_sampling_frequency(),
                "buffer type": self.read_buffer_type(),
                "ADC line sync": self.read_sync_filter(),
                }
