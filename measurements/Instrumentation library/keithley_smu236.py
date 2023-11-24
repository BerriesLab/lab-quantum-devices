import numpy as np
import time
from collections import defaultdict


class smu236():

    # region dictionary for SCPI communication
    scpi_w = {"sens": {"remote": "1",
                       "local": "0"},
              "sour": {"i": "1",
                       "v": "0"},
              "func": {"dc": "0",
                       "sweep": "1"},
              "filt": {0: "0",
                       2: "1",
                       4: "2",
                       8: "3",
                       16: "4",
                       32: "5"},
              "oper": {"on": "1",
                       "off": "0"},
              "time": {416E-6: "0",
                       4E-3: "1",
                       16.67E-3: "2",
                       20E-3: "3"},
              "rang_sour": {"i": {"auto": "00",
                                  1E-9: "01",
                                  1E-8: "02",
                                  1E-7: "03",
                                  1E-6: "04",
                                  1E-5: "05",
                                  1E-4: "06",
                                  1E-3: "07",
                                  1E-2: "8",
                                  1E-1: "9"},
                            "v": {"auto": "00",
                                  1.1: "01",
                                  11: "02",
                                  110: "03"}},
              "rang_sens": {"i": {"auto": "00",
                                  1E-9: "01",
                                  1E-8: "02",
                                  1E-7: "03",
                                  1E-6: "04",
                                  1E-5: "05",
                                  1E-4: "06",
                                  1E-3: "07",
                                  1E-2: "08",
                                  1E-1: "09"},
                            "v": {"auto": "00",
                                  1.1: "01",
                                  11: "02",
                                  110: "03"}},
              "points_per_decade": {5: 0,
                                    10: 1,
                                    25: 2,
                                    50: 3},
              "offs": {"off": "0",
                       "on": "1"},
              "srqm": {"mask cleared": "000",
                       "warning": "001",
                       "sweep done": "002",
                       "trigger out": "004",
                       "reading done": "008",
                       "ready for trigger": "016",
                       "error": "032",
                       "compliance": "128"},
              "trig": {"status": {"enabled": 1,
                                  "disabled": 0},
                       "origin": {"ieee X": 0,
                                  "ieee get": 1,
                                  "ieee talk": 2,
                                  "external": 3,
                                  "immediate": 4},
                       "input": {"continuous": 0,
                                 "^src dly msr": 1,
                                 "src ^dly msr": 2,
                                 "^src ^dly msr": 3,
                                 "src dly ^msr": 4,
                                 "^src dly ^msr": 5,
                                 "src ^dly ^msr": 6,
                                 "^src ^dly ^msr": 7,
                                 "single pulse": 8},
                       "output": {"none": 0,
                                  "src^ dly msr": 1,
                                  "src dly^ msr": 2,
                                  "src^ dly^ msr": 3,
                                  "src dly msr^": 4,
                                  "src^ dly msr^": 5,
                                  "src dly^ msr^": 6,
                                  "src^ dly^ msr^": 7,
                                  "pulse end": 8},
                       "end": {"disabled": 0,
                               "enabled": 1}}}
    # endregion

    # region SCPI dictionary for reading from instrumentation
    scpi_r = defaultdict(dict)
    for key, val in scpi_w.items():
        for subkey, subval in val.items():
            if type(subval) is type(dict()):
                scpi_r[key][subkey] = defaultdict(dict)
                for subsubkey, subsubval in subval.items():
                    scpi_r[key][subkey][subsubval] = subsubkey
            else:
                scpi_r[key][subval] = subkey
    # endregion

    # region other dictionaries
    default_delay = {1E-9: 0.360,
                     10E-9: 0.075,
                     100E-9: 0.020,
                     1E-6: 0.005,
                     10E-6: 0.002,
                     100E-6: 0,
                     1E-3: 0,
                     10E-3: 0,
                     100E-3: 0,
                     1: 0,
                     "auto": None}
    # endregion

    '''----- Initialize object -----'''

    def __init__(self, visa):

        self.visa = visa
        self.visa.timeout = None

        # Wait after read / write
        self.wait = 0.01

        self.model = self.read_model()

        # Restore factory defaults of smu
        self.visa.write("J0X")
        time.sleep(self.wait)

        # put unit in standby
        self.visa.write("N0X")
        time.sleep(self.wait)

    '''----- Set settings functions -----'''

    def set_filter(self, samples=0):
        # set samples
        self.visa.write("P{}X".format(self.scpi_w["filt"][samples]))
        time.sleep(self.wait)

    def set_sensing(self, sensing="local"):
        # set sensing to local or remote
        self.visa.write("O{}X".format(self.scpi_w["sens"][sensing]))
        time.sleep(self.wait)

    def set_integration_time(self, integration_time=416e-6):
        # set the integration time (nlpc)
        self.visa.write("S{}X".format(self.scpi_w["time"][integration_time]))
        time.sleep(self.wait)

    def set_srq_mask(self, srq_mask="sweep done"):
        # Set the SRQ mask: M(mask}, (compliance), where mask = 2 is for sweep done, and mask = is for reading available
        self.visa.write("M{},0X".format(self.scpi_w["srqm"][srq_mask]))
        time.sleep(self.wait)

    def set_sense_range(self, range):
        # set the sense range
        sense = self.read_sense().lower()
        self.visa.write("L,{}X".format(self.scpi_w["rang_sens"][sense][range]))
        time.sleep(self.wait)

    def set_compliance(self, level="auto"):
        # set compliance value.
        # If sense range is "auto" the compliance is hardware adjusted, so pass
        # else, set compliance to level
        if self.read_sense_range() == "auto":
            pass
        else:
            self.visa.write("L{},X".format(level))
        time.sleep(self.wait)

    def set_source(self, source):
        # set source to "i" or "v"
        self.visa.write("F{},X".format(self.scpi_w["sour"][source]))
        time.sleep(self.wait)

    def set_function(self, function):
        # set function to "dc" or "sweep".
        # Note: only "dc" is compatible with continuous operation
        self.visa.write("F,{}X".format(self.scpi_w["func"][function]))
        time.sleep(self.wait)

    def set_trigger_on(self):
        # switch trigger on
        self.visa.write("R1X")
        time.sleep(self.wait)

    def set_trigger_off(self):
        # switch trigger on
        self.visa.write("R0X")
        time.sleep(self.wait)

    def set_trigger_control(self, origin="immediate", trigger_in="continuous", trigger_out="none", trigger_end="disabled"):
        # set trigger settings. Origin = 4 allow trigger over the bus
        # Note: it is recommended to switch off the trigger before changing the settings, and then turn it on again
        self.visa.write("T{},{},{},{}X".format(self.scpi_w["trig"]["origin"][origin], self.scpi_w["trig"]["input"][trigger_in],
                                               self.scpi_w["trig"]["output"][trigger_out], self.scpi_w["trig"]["end"][trigger_end]))
        time.sleep(self.wait)

    def set_suppress_on(self):
        # switch suppress on
        self.visa.write("Z1X")
        time.sleep(self.wait)

    def set_suppress_off(self):
        # switch suppress on
        self.visa.write("Z0X")
        time.sleep(self.wait)

    def set_default_delay(self, status="on"):
        if status == "on":
            self.visa.write("W1X")
        elif status == "off":
            self.visa.write("W0X")
        time.sleep(self.wait)

    ''' ----- Read settings functions -----'''

    def read_sense(self):
        # read sense setting
        val = self.visa.query("U4X")[0].lower()
        time.sleep(self.wait)
        return val

    def read_sense_range(self):
        # read sense range. Returns a float
        sense = self.read_sense()
        val = self.scpi_r["rang_sens"][sense][self.visa.query("U4X")[5:7]]
        time.sleep(self.wait)
        return val

    def read_source(self):
        # read source
        val = self.scpi_r["sour"][self.visa.query("U4X")[8:9].lower()]
        time.sleep(self.wait)
        return val

    def read_function(self):
        # read source function
        val = self.scpi_r["func"][self.visa.query("U4X")[10]]
        time.sleep(self.wait)
        return val

    def read_filter(self):
        # read filter
        val = self.scpi_r["filt"][self.visa.query("U4X")[14]]
        time.sleep(self.wait)
        return val

    def read_sensing(self):
        # read sensing
        val = self.scpi_r["sens"][self.visa.query("U4X")[12]]
        time.sleep(self.wait)
        return val

    def read_integration_time(self):
        # read integration time
        val = self.scpi_r["time"][self.visa.query("U4X")[16]]
        time.sleep(self.wait)
        return val

    def read_srq_mask(self):
        # read service request enable register (mask).
        # Note: returns a decimal number that is the sum of the decimal representation of the active registers
        val = self.scpi_r["srqm"][self.visa.query("U3X")[13:16]]
        time.sleep(self.wait)
        return val

    def read_compliance(self):
        # read compliance level
        val = float(self.visa.query("U5X")[3:])
        time.sleep(self.wait)
        return val

    def read_model(self):
        # read unit model
        val = self.visa.query("U0X").strip("\n")
        time.sleep(self.wait)
        return val

    def read_default_delay(self):
        # check if default delay is active and return delay in ms
        val = int(self.visa.query("U4X")[18])
        time.sleep(self.wait)
        if val == 0:
            return 0
        else:
            sense_range = self.read_sense_range()
            return self.default_delay[sense_range]

    '''----- Operation functions -----'''

    def switch_on(self):
        # turn "operate" on
        # DC Operation- With the de function selected, enabling operate will apply the source to the output. If the MANUAL TRIGGER light is blinking,
        # a trigger is needed to start making measurements.
        # Sweep Operation - With the sweep function selected, enabling OPERATE will source (but not measure) the bias level of the sweep.
        # The sweep itself will not start until the appropriate trigger occurs (as denoted by the blinking MANUAL TRIGGER light).
        self.visa.write("N1X")
        time.sleep(self.wait)

    def switch_off(self):
        # turn "operate" off and put unit into idle
        self.visa.write("N0X")
        time.sleep(self.wait)

    def set_bias_level(self, bias, delay=0):
        # Set dc operation and bias level
        self.visa.write("B{},,X".format(bias))
        time.sleep(self.wait)
        time.sleep(delay)

    def set_bias_range(self, bias_range):
        # Set dc operation and bias range
        source = self.read_source()
        self.visa.write("B,{},X".format(self.scpi_w["rang_sour"][source][bias_range]))
        time.sleep(self.wait)

    def set_bias_delay(self, delay):
        # Set dc operation and delay in
        self.visa.write("B,,{}X".format(delay))
        time.sleep(self.wait)

    def read(self):
        # read last measurement in memory
        data = self.visa.query("G5,2,0X")
        time.sleep(self.wait)
        source = float(data.split(",")[0])
        measure = float(data.split(",")[1])
        return source, measure

    def read_buffer(self):
        # query format is: G(items) ,(format) ,(lines)
        # items (sum decimal values): O = No items,
        #                             1 = Source value,
        #                             2 = Delay value,
        #                             4 = Measure value
        #                             8 = Time value
        # format: 0 = ASCII data with prefix and suffix,
        #         1 = ASCIT data with prefix, no suffix,
        #         2 = ASCIT data, no prefix or suffix,
        #         3 = HP binary data,
        #         4 = ffiM binary data
        # lines: 0 = One line of data per talk,
        #        1 = One line of sweep data per talk,
        #        2 = All lines of sweep data per talk
        data = np.array([float(x) for x in self.visa.query("G5,2,2X").strip("\r\n").split(",")])
        time.sleep(self.wait)
        measure = data[1::2]
        source = data[::2]
        return source, measure

    def create_linear_staircase(self, start, stop, step, source_range="auto", delay=0):
        # Note: delay is in ms, and the maximum number of steps is 1000. More steps will raise a buffer full error
        # The function stores data in the unit buffer and does not return any value.
        source = self.read_source()
        time.sleep(self.wait)
        # create linear staircase (Q1)
        self.visa.write("Q1,{},{},{},{},{}X".format(start, stop, step, self.scpi_w["rang_sour"][source][source_range], delay))
        time.sleep(self.wait)

    def append_linear_staircase(self, start, stop, step, source_range="auto", delay=0):
        source = self.read_source()
        self.visa.write("Q7,{},{},{},{},{}X".format(start, stop, step, self.scpi_w["rang_sour"][source][source_range], delay))
        time.sleep(self.wait)

    def create_fixed_staircase(self, level, source_range="auto", delay=0, count=1):
        # Note: delay is in ms, and the maximum number of steps is 1000. More steps will raise a buffer full error
        # The function stores data in the unit buffer and does not return any value.
        source = self.read_source()
        time.sleep(self.wait)
        self.visa.write("Q0,{},{},{},{}X".format(level, self.scpi_w["rang_sour"][source][source_range], delay, count))
        time.sleep(self.wait)

    def append_fixed_staircase(self, level, source_range="auto", delay=0, count=1):
        source = self.read_source()
        time.sleep(self.wait)
        self.visa.write("Q6,{},{},{},{}X".format(level, self.scpi_w["rang_sour"][source][source_range], delay, count))
        time.sleep(self.wait)

    def create_logarithmic_staircase(self, start, stop, points_decade, source_range="auto", delay=0):
        # Note: delay is in ms, and the maximum number of steps is 1000. More steps will raise a buffer full error
        # A log sweep cannot start at 0 or sweep through 0: start must be different from 0
        # The function stores data in the unit buffer and does not return any value.
        source = self.read_source()
        time.sleep(self.wait)
        # create linear staircase (Q1)
        self.visa.write("Q2,{},{},{},{},{}X".format(start, stop, self.scpi_w["points_per_decade"][points_decade], self.scpi_w["rang_sour"][source][source_range], delay))
        time.sleep(self.wait)

    def append_logarithmic_staircase(self, start, stop, points_decade, source_range="auto", delay=0):
        source = self.read_source()
        time.sleep(self.wait)
        self.visa.write("Q8,{},{},{},{},{}X".format(start, stop, self.scpi_w["points_per_decade"][points_decade], self.scpi_w["rang_sour"][source][source_range], delay))
        time.sleep(self.wait)

    def program_iv(self, source, start, stop, step, mode=0, type="lin",
                   source_range="auto", sense_range="auto", delay=0, samples=0, integration_time=20e-3, sensing="local", compliance="auto", srq_mask="sweep done",
                   trigger_origin="immediate", trigger_in="continuous", trigger_out="none", trigger_end="disabled"):
        # Program an iv measurement in unit's hardware that is activated upon receiving a trigger.
        # mode: 0 = forward scan only,
        #       1 = forward and backward scan,
        #       2 = hysteresis-like scan
        self.set_source(source)
        self.set_function("sweep")
        self.set_sense_range(sense_range)
        self.set_filter(samples)
        self.set_integration_time(integration_time)
        self.set_sensing(sensing)
        self.set_compliance(compliance)
        self.set_srq_mask(srq_mask)
        self.set_trigger_off()
        self.set_trigger_control(trigger_origin, trigger_in, trigger_out, trigger_end)
        self.set_trigger_on()
        if type == "lin":
            if mode == 0:
                self.create_linear_staircase(start, stop, step, source_range, delay)
            elif mode == 1:
                self.create_linear_staircase(start, stop, step, source_range, delay)
                self.append_linear_staircase(stop - step, start, step, source_range, delay)
            elif mode == 2:
                self.create_linear_staircase(start, stop, step, source_range, delay)
                self.append_linear_staircase(stop - step, stop - 2 * (stop - start), step, source_range, delay)
                self.append_linear_staircase(stop - 2 * (stop - start) + step, start, step, source_range, delay)
        elif type == "log":
            print("Not yet implemented")
 
    def make_iv(self, source, start, stop, step, mode=0, type="lin",
                source_range="auto", sense_range="auto", delay=0, samples=0, integration_time=20e-3, sensing="local", compliance="auto", suppress=False):
        # Make an iv and return measurement data
        self.program_iv(source, start, stop, step, mode, type, source_range, sense_range, delay, samples, integration_time, sensing, compliance)
        self.switch_on()
        if suppress is True:
            self.set_suppress_on()
        self.send_trigger()
        self.wait_for_srq()
        buffer = self.read_buffer()
        if suppress is True:
            self.set_suppress_off()
        return buffer

    def program_bias(self, source, output_value, source_range="auto", sense_range="auto", delay=0, samples=0, integration_time=20e-3, sensing="local",
                     compliance="auto"):
        # program a bias operation to source a dc value. Requires a trigger over the bus to initiate
        self.set_srq_mask()
        self.set_trigger_off()
        self.set_trigger_control()
        self.set_trigger_on()
        self.set_source(source)
        self.set_bias_range(source_range)
        self.set_bias_level(output_value)
        self.set_bias_delay(delay)
        self.set_sense_range(sense_range)
        self.set_filter(samples)
        self.set_integration_time(integration_time)
        self.set_sensing(sensing)
        self.set_compliance(compliance)

    def bias(self, source, output_value, source_range="auto", sense_range="auto", delay=0, samples=0, integration_time=20e-3, sensing="local", compliance="auto"):
        self.program_bias(source, output_value, source_range, sense_range, delay, samples, integration_time, sensing, compliance)
        self.switch_on()
        self.send_trigger()

    def sweep_bias(self, source, start, stop, n_step, rate, source_range, sense_range, compliance="auto", samples=0, integration_time=20e-3, sensing="local"):
        # Sweep source from "start" to "end" with step "(end-start)/step" and rate "rate" (in unit/s)
        # Depending on the settings of the keithley, the actual rate could be slower.
        if abs((stop-start)/n_step)/rate > self.wait:
            actual_wait = abs((stop-start)/n_step)/rate - self.wait
        else:
            actual_wait = 0
        self.program_bias(source, start, source_range, sense_range, 0, samples, integration_time, sensing, compliance)
        self.switch_on()
        self.send_trigger()
        if start != stop:
            for val in np.linspace(start, stop, n_step):
                self.set_bias_level(val)
                time.sleep(actual_wait)

    def wait_for_srq(self, timeout=None):
        # wait for unit to raise a service request
        self.visa.wait_for_srq(timeout=timeout)

    def send_trigger(self):
        # send a trigger to the unit over the bus
        self.visa.write("H0X")

    def get_settings(self):
        return {"smu unit": self.read_model(),
                "source": self.read_source(),
                "sense": self.read_sense(),
                "sensing": self.read_sensing(),
                "sense range": self.read_sense_range(),
                "compliance": self.read_compliance(),
                "samples": self.read_filter(),
                "integration time": self.read_integration_time()}
