import numpy as np
import time
import struct
from collections import defaultdict

class dc205():

    scpi_w = {"range": {1: "0",
                        10: "1",
                        100: "2"},
              "isolation": {"ground": "0",
                            "float": "1"},
              "sensing": {"local": "0",
                          "remote": "1"},
              "output": {"off": "0",
                         "on": "1"},
              "token": {"off": "0",
                        "on": "1"}
              }

    # SCPI dictionary for reading from instrumentation
    scpi_r = defaultdict(dict)
    for key, val in scpi_w.items():
        for subkey, subval in val.items():
            scpi_r[key][subval] = subkey

    def __init__(self, visa, wait=0.01, reset=True):
        # create an empty local registry and populate the registry with the current instrumentation settings
        # when adding/removing parameters, amend "get_settings" method
        self.visa = visa
        self.wait = wait
        self.model = self.read_model()
        self.visa.read_termination = "\r\n"

        if reset is True:
            self.visa.write("*rst")

    '''----- Set functions -----'''

    def set_range(self, sense_range):
        # sense range is int and can be 1, 10, or 100
        status = self.read_output_status()
        if status == "on":
            print("Cannot change range while output is on")
        if self.read_output_status() == "off":
            self.visa.write("rnge {}".format(self.scpi_w["range"][sense_range]))
            time.sleep(self.wait)

    def set_isolation(self, isolation):
        # isolation can be "ground" or "float"
        self.visa.write("isol {}".format(isolation))
        time.sleep(self.wait)

    def set_sensing(self, sensing="local"):
        self.visa.write("sens {}".format(self.scpi_w["sensing"][sensing]))
        time.sleep(self.wait)

    def set_output_status(self, status):
        # status can be either "on" or "off"
        # The voltage source output is enabled or disabled using the SOUT
        # command. When set to SOUT OFF, the OUTPUT HI terminal is
        # disconnected from the output circuitry. If the source is configured
        # for ISOL GROUND, then the OUTPUT LO terminal remains connected
        # to chassis ground.
        # If the source range is set to RANG RANGE1 or RANG RANGE10, then
        # SOUT ON may be sent at any time. However, if the source range is set
        # to RANG RANGE100, then SOUT ON may only be sent while the safety
        # interlock is closed.
        # The SOUT command is equivalent to pressing the OUTPUT [On/Off] button
        self.visa.write("sout {}".format(self.scpi_w["output"][status]))

    def set_output_level(self, level):
        self.visa.write("volt {:0.6f}".format(level))
        time.sleep(self.wait)

    def set_token(self, token="off"):
        self.visa.write("tokn {}".format(self.scpi_w["token"][token]))
        time.sleep(self.wait)

    def set_srq_enable_register(self, val):
        # val is the sum of the decimal representation of each active bit
        self.visa.write("*sre {}".format(val))
        time.sleep(self.wait)

    '''----- Read functions -----'''

    def read_range(self):
        val = self.scpi_r["range"][self.visa.query("rnge?").lower()]
        time.sleep(self.wait)
        return val

    def read_isolation(self):
        # isolation can be "ground" or "float"
        val = self.scpi_r["isolation"][self.visa.query("isol?")]
        time.sleep(self.wait)
        return val

    def read_output_status(self):
        val = self.scpi_r["output"][self.visa.query("sout?")]
        time.sleep(self.wait)
        return val

    def read_model(self):
        val = self.visa.query("*idn?")
        time.sleep(self.wait)
        return val

    def read_status_byte_register(self):
        val = self.visa.query("*stb?")
        time.sleep(self.wait)
        return val

    def read_srq_enable_register(self):
        val = self.visa.query("*sre?")
        time.sleep(self.wait)
        return val

    ''' ----- Operation functions ----- '''

    def reset_unit(self):
        self.visa.write("*rst")
        time.sleep(self.wait)

    def clear_all_event_status_registers(self):
        self.visa.write("*cls")
        time.sleep(self.wait)

    def sweep_bias(self, start, stop, n_step=100, rate=10e-6):
        # run through all the output voltage values
        if start != stop:
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
            if (abs((stop - start) / nstep) + 1) / rate > self.wait:
                delay = (abs((stop - start) / nstep) + 1) / rate
            else:
                delay = self.wait
            for v in np.linspace(start, stop, nstep):
=======
            actual_wait = np.max([self.wait, abs(stop - start) / n_step / rate])
            for v in np.linspace(start, stop, n_step, endpoint=True):
>>>>>>> parent of 3fda7e2 (major)
=======
            actual_wait = np.max([self.wait, abs(stop - start) / n_step / rate])
            for v in np.linspace(start, stop, n_step, endpoint=True):
>>>>>>> parent of 3fda7e2 (major)
=======
            actual_wait = np.max([self.wait, abs(stop - start) / n_step / rate])
            for v in np.linspace(start, stop, n_step, endpoint=True):
>>>>>>> parent of 3fda7e2 (major)
=======
            actual_wait = np.max([self.wait, abs(stop - start) / n_step / rate])
            for v in np.linspace(start, stop, n_step, endpoint=True):
>>>>>>> parent of 3fda7e2 (major)
                self.set_output_level(v)
                # wait "time" seconds before increasing the voltage level
                time.sleep(actual_wait)

    def configure(self, source_range=1, isolation="float", sensing="local"):
        self.set_range(source_range)
        self.set_isolation(isolation)
        self.set_sensing(sensing)

    def program_bias(self, output_value=0, source_range=1, isolation="float", sensing="local"):
        self.configure(source_range, isolation, sensing)
        self.set_output_level(output_value)

    def bias(self, output_value=0, source_range=1, isolation="float", sensing="local"):
        self.program_bias(output_value, source_range, isolation, sensing)
        self.set_output_status("on")

    def get_settings(self):
        return {"unit": self.read_model(),
                "sense range": self.read_range(),
                "isolation": self.read_isolation(),
                }
