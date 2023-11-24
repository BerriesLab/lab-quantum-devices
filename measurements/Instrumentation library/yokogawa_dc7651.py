import time
import numpy as np
from collections import defaultdict


class dc7651():

    # SCPI dictionary for writing to instrumentation (refer to manual)
    scpi_w = {"function": {"v": "1",
                           "i": "5"},
              "range": {"v": {0.01: "2",
                              0.1: "3",
                              1: "4",
                              10: "5",
                              30: "6"},
                        "i": {0.001: "4",
                              0.01: "5",
                              0.1: "6"}
                        },
              "output_state": {"off": "O0",
                               "on": "O1"},
              "polarity": {"+": "0",
                           "-": "1",
                           "invert": "2"},
              "mode": {"single": "1",
                       "repeat": "0"}
              }

    # SCPI dictionary for reading from instrumentation
    scpi_r = defaultdict(dict)
    for key, val in scpi_w.items():
        for subkey, subval in val.items():
            if type(subval) is type(dict()):
                scpi_r[key][subkey] = defaultdict(dict)
                for subsubkey, subsubval in subval.items():
                    scpi_r[key][subkey][subsubval] = subsubkey
            else:
                scpi_r[key][subval] = subkey

    def __init__(self, visa, wait=0.01):
        self.visa = visa
        self.reset_unit()
        # self.model =

    ''' ----- Set functions ----- '''

    def set_function(self, function):
        # function can be either "i" or "v"
        self.visa.write("F{}".format(self.scpi_w["function"][function]))
        time.sleep(self.wait)

    def set_range(self, function, source_range):
        self.visa.write("R{}".format(self.scpi_w["range"][function][source_range]))
        time.sleep(self.wait)

    def set_output_level(self, level):
        self.visa.write("S{}".format(level))
        time.sleep(self.wait)

    def set_mode(self, mode):
        self.visa.write("M{}".format(mode))
        time.sleep(self.wait)

    def set_voltage_compliance(self, level):
        # value in Volts
        self.visa.write("LV{}".format(level))
        time.sleep(self.wait)

    def set_current_compliance(self, level):
        # value in mA
        self.visa.write("LA{}".format(level))
        time.sleep(self.wait)

    def set_polarity(self, polarity):
        self.visa.write("SG{}".format(polarity))
        time.sleep(self.wait)

    ''' ----- Read functions ----- '''

    ''' ----- Operation functions ----- '''

    def switch_on(self):
        # a trigger is required to execute the commands
        self.visa.write("O1")
        time.sleep(self.wait)
        self.send_trigger()

    def switch_off(self):
        # a trigger is required to execute the commands
        self.visa.write("O0")
        time.sleep(self.wait)
        self.send_trigger()

    def send_trigger(self):
        self.visa.write("E")

    def reset_unit(self):
        self.visa.write("RC")

    def configure(self, function="v", source_range=10e-3, voltage_compliance=1, current_compliance=1, polarity="+", mode="single"):
        # DC source configuration
        self.set_function(self.scpi_w["function"][function])
        self.set_range(self.scpi_w["range"][source_range])
        self.set_voltage_compliance(voltage_compliance)
        self.set_current_compliance(current_compliance)
        self.set_polarity(polarity)
        self.set_output_level(0)
        self.set_mode(mode)
        self.send_trigger()

    def set_output(self, level):
        # set output level, switch on unit and send trigger to execute
        self.set_output_level(level)
        self.switch_on()
        self.send_trigger()

    def sweep_output(self, start, stop, n_step, rate):
        self.set_output_level(start)
        self.switch_on()
        self.send_trigger()
        time.sleep(self.wait)
        for level in np.linspace(start, stop, n_step, endpoint=True):
            self.set_output_level(level)
            self.send_trigger()
            if self.wait() < abs(start - stop) / n_step / rate:
                # wait an additional time to make the total time wait corresponding to the chosen wait
                time.sleep(abs(start - stop) / n_step / rate - self.wait)
            else:
                # self.wait (inside set_output_level) becomes the actual waiting time, upper limiting the rate
                continue


