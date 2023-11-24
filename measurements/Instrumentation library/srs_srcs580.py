import numpy as np
import time
from collections import defaultdict


class srcs580:

    """ Class of Stanford Research Systems srcs580. """

    # SCPI dictionary for writing to instrumentation (refer to manual)
    scpi_w = {"gain": {1E-9: "0", 10E-9: "1", 100E-9: "2", 1E-6: "3", 10E-6: "4", 100E-6: "5", 1E-3: "6", 10E-3: "7", 50E-3: "8"},
              "inpt": {"off": "0", "on": "1"},
              "resp": {"fast": "0", "slow": "1"},
              "shld": {"guard": "0", "return": "1"},
              "isol": {"ground": "0", "float": "1"},
              "sout": {"off": "0", "on": "1"},
              "curr": {"ok": "0", "overload": "1"}}

    # SCPI dictionary for reading from instrumentation
    scpi_r = defaultdict(dict)
    for key, val in scpi_w.items():
        for subkey, subval in val.items():
            scpi_r[key][subval] = subkey

    def __init__(self, visa, wait=0.01):

        self.visa = visa
        self.wait = wait
        self.model = self.read_model()
        self.operation("off", "off")

    ''' ----- Set functions -----'''

    def set_gain(self, gain):
        self.visa.write("GAIN {}".format(self.scpi_w["gain"][gain]))
        time.sleep(self.wait)

    def set_response(self, response):
        # set bandwidth between "fast" or "slow"
        self.visa.write("RESP {}".format(self.scpi_w["resp"][response]))
        time.sleep(self.wait)

    def set_shield(self, shield):
        self.visa.write("SHLD {}".format(self.scpi_w["shld"][shield]))
        time.sleep(self.wait)

    def set_isolation(self, isolation):
        self.visa.write("ISOL {}".format(self.scpi_w["isol"][isolation]))
        time.sleep(self.wait)

    def set_compliance(self, compliance):
        self.visa.write("VOLT {}".format(compliance))
        time.sleep(self.wait)

    def set_input_state(self, state):
        self.visa.write("INPT {}".format(self.scpi_w["inpt"][state]))
        time.sleep(self.wait)

    def set_output_state(self, state):
        self.visa.write("SOUT {}".format(self.scpi_w["sout"][state]))
        time.sleep(self.wait)

    ''' ----- Read functions -----'''

    def read_gain(self):
        val = self.scpi_r["gain"][self.visa.query("GAIN?").strip("\n").strip("\r")]
        time.sleep(self.wait)
        return val

    def read_response(self):
        val = self.scpi_r["resp"][self.visa.query("RESP?").strip("\n").strip("\r")]
        time.sleep(self.wait)
        return val

    def read_shield(self):
        val = self.scpi_r["shld"][self.visa.query("SHLD?").strip("\n").strip("\r")]
        time.sleep(self.wait)
        return val

    def read_isolation(self):
        val = self.scpi_r["isol"][self.visa.query("ISOL?").strip("\n").strip("\r")]
        time.sleep(self.wait)
        return val

    def read_compliance(self):
        val = float(self.visa.query("VOLT?").strip("\n").strip("\r"))
        time.sleep(self.wait)
        return val

    def read_model(self):
        val = self.visa.query("*IDN?").rstrip()
        time.sleep(self.wait)
        return val

    def read_overload_status(self):
        val = int(self.visa.query("ovld?").strip("\n").strip("\r"))
        return val

    '''----- Operation functions -----'''

    def reset_factory_default(self):
        self.visa.write("*RST")
        time.sleep(self.wait)

    def operation(self, input_state, output_state):
        self.set_input_state(input_state)
        self.set_output_state(output_state)

    def set_current(self, val):
        self.visa.write(f"CURR {val}")

    def configure(self, gain=10e-3, response="fast", shield="return", isolation="float", input_state="off", output_state="off", compliance=50):
        self.reset_factory_default()
        self.set_gain(gain)
        self.set_response(response)
        self.set_shield(shield)
        self.set_isolation(isolation)
        self.set_compliance(compliance)
        self.operation(input_state, output_state)

    def sweep_current(self, start, stop, nstep, rate):
        if start != stop:
            if (abs((stop - start) / nstep) + 1) / rate > self.wait:
                delay = abs((stop - start) / nstep) / rate
            else:
                delay = self.wait
            for val in np.linspace(start, stop, nstep):
                self.set_current(val)
                time.sleep(delay)

    def get_settings(self):
        return {"unit": self.read_model(),
                "gain": self.read_gain(),
                "response": self.read_response(),
                "shield": self.read_shield(),
                "isolation": self.read_isolation(),
                "compliance": self.read_compliance()}
