import time
from collections import defaultdict


class tc336():

    """ Instrumentation drivers """

    # SCPI dictionary for writing to instrumentation (refer to manual)
    scpi_w = {"range": {"off": "0", "low": "1", "medium": "2", "high": "3"},
              "filter": {"on": "1", "off": "0"},
              "read": {"all": "0", "a": "1", "b": "2", "c": "3", "d": "4"}}

    # SCPI dictionary for reading from instrumentation
    scpi_r = defaultdict(dict)
    for key, val in scpi_w.items():
        for subkey, subval in val.items():
            scpi_r[key][subval] = subkey

    def __init__(self, visa, wait=0.01, t_switch_range=50):
        # create an empty local registry and populate the registry with the current instrumentation settings
        # when adding/removing parameters, amend "get_settings" method

        self.visa = visa
        self.wait = wait
        self.t_switch_range = t_switch_range
        self.model = self.read_model()
        # self.visa.write("*rst")  # reset controller parameters to power-up settings

    '''----- Set functions ------'''

    def set_filter(self, channel, state, samples, window=2):
        # channel is "a", "b", "c" or "d"
        # state is "on" or "off"
        # max samples value = 64
        self.visa.write("filter {},{},{},{}".format(channel, self.scpi_w["filter"][state], samples, window))
        time.sleep(self.wait)

    def set_heater_range(self, heater, range):
        # heater is 1 or 2
        # range is "off", "low", "medium", or "high"
        self.visa.write("range {},{}".format(heater, self.scpi_w["range"][range]))
        time.sleep(self.wait)

    def set_pid(self, pid, p, i, d):
        # pid is 1 or 2
        self.visa.write("pid {},{},{},{}".format(pid, p, i, d))
        time.sleep(self.wait)

    def set_temperature(self, output, setpoint):
        # set temperature setpoint.
        # Note: output can be either 1 (stage) or 2 (shield), and t is in kelvin
        if setpoint < self.t_switch_range:
            self.set_heater_range(1, "medium")
            self.set_heater_range(2, "medium")
        elif setpoint >= self.t_switch_range:
            self.set_heater_range(1, "high")
            self.set_heater_range(2, "high")
        self.visa.write("SETP {},{}".format(output, setpoint))
        time.sleep(self.wait)

    '''----- Read functions -----'''

    def read_filter(self, channel):
        # return samples, window
        val = self.visa.query("filter? {}".format(channel)).split(",")
        time.sleep(self.wait)
        return val

    def read_heater_range(self, channel):
        val = self.scpi_r["range"][self.visa.query("range? {}".format(channel)).strip("\n").strip("\r")]
        time.sleep(self.wait)
        return val

    def read_pid(self, pid):
        # return p, i , d
        val = [float(x) for x in self.visa.query("pid? {}".format(pid)).split(",")]
        time.sleep(self.wait)
        return val

    def read_model(self):
        # return model number
        val = self.visa.query("*IDN?").rstrip()
        time.sleep(self.wait)
        return val



    '''----- Operation functions -----'''

    def read_temperature(self, sensor="all"):
        # read temperature from sensors ("all", "a", "b", "c" or "d")
        if sensor == "all":
            val = [float(x) for x in self.visa.query("KRDG? {}".format(self.scpi_w["sensor"][sensor])).split(",")]
        else:
            val = float(self.visa.query("KRDG? " + self.scpi_w["sensor"][sensor]))
        time.sleep(self.wait)
        return val

    def warm_up(self):
        # set stage and shield temperature setpoint(s) to room temperature
        self.visa.write("SETP 1, 300")
        time.sleep(self.wait)
        self.visa.write("SETP 2, 300")
        time.sleep(self.wait)

    def off(self):
        # switch stage and shield heaters off
        self.visa.write("range 1, off")
        time.sleep(self.wait)
        self.visa.write("range 2, off")
        time.sleep(self.wait)

    def configure(self, range_heater_1="high", range_heater_2="high", filter_state="on", filter_samples=64,
                  filter_window=2, p1=75, i1=15, d1=0, p2=50, i2=20, d2=0):
        self.set_filter("a", filter_state, filter_samples, filter_window)
        self.set_filter("b", filter_state, filter_samples, filter_window)
        self.set_filter("c", filter_state, filter_samples, filter_window)
        self.set_filter("d", filter_state, filter_samples, filter_window)
        self.set_heater_range(1, range_heater_1)
        self.set_heater_range(2, range_heater_2)
        self.set_pid(1, p1, i1, d1)
        self.set_pid(2, p2, i2, d2)

    def get_settings(self):
        return {"model": self.read_model(),
                "filter channel a (state, samples, window)": self.read_filter("a"),
                "filter channel b (state, samples, window)": self.read_filter("b"),
                "filter channel c (state, samples, window)": self.read_filter("c"),
                "filter channel d (state, samples, window)": self.read_filter("d"),
                "heater 1 range": self.read_heater_range(1),
                "heater 2 range": self.read_heater_range(1),
                "pid 1 settings (p, i, d)": self.read_pid(1),
                "pid 2 settings (p, i, d)": self.read_pid(2),
                }

