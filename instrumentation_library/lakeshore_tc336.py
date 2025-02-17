import time
import pyvisa
from collections import defaultdict


class Lakeshore336:
    """ A class to control a Lakeshore336 temperature controller. """

    # Helper SCPI dictionary for writing to instrumentation
    scpi_w = {"range": {"off": "0", "low": "1", "medium": "2", "high": "3"},
              "filter": {"on": "1", "off": "0"},
              "read": {"all": "0", "a": "1", "b": "2", "c": "3", "d": "4"}}

    # Helper SCPI dictionary for reading from instrumentation
    scpi_r = defaultdict(dict)
    for key, val in scpi_w.items():
        for subkey, subval in val.items():
            scpi_r[key][subval] = subkey

    # Waiting time after command - Should be improved with a handshake check.
    wait: float = 0.01

    # Set temperature threshold (in K) between heater range "high" and "medium".
    t_switch: float = 50.0,

    # Initialize instance
    def __init__(
            self,
            visa: pyvisa,
            address: str = "ASRL8::INSTR",
            sampling_freq: int = 1,
            settling_time_init: float = 0.1 * 1 * 60,
            settling_time: float = 0.1 * 1 * 60
    ):
        self.model = self.read_model()
        self.visa = visa  # VISA address
        self.address = address  # Address of temperature controller
        self.sampling_freq = sampling_freq  # Temperature sampling frequency (in Hz)
        self.settling_time_init = settling_time_init  # Cryostat thermalization time (in s).
        self.settling_time = settling_time  # Cryostat thermalization time (in s).

    def reset_controller_to_default_settings(self):
        """ Reset controller parameters to power-up settings. """
        self.visa.write("*rst")

    def set_filter(self, channel, state, samples, window=2):
        # channel is "a", "b", "c" or "d"
        # state is "on" or "off"
        # max samples value = 64
        self.visa.write(f"filter {channel},{self.scpi_w["filter"][state]},{samples},{window}")
        time.sleep(self.wait)

    def set_heater_range(self, heater, heater_range):
        # heater is 1 or 2
        # range is "off", "low", "medium", or "high"
        self.visa.write(f"range {heater},{self.scpi_w["range"][heater_range]}")
        time.sleep(self.wait)

    def set_pid(self, pid, p, i, d):
        # pid is 1 or 2
        self.visa.write(f"pid {pid},{p},{i},{d}")
        time.sleep(self.wait)

    def set_temperature(self, output, setpoint):
        # set temperature setpoint.
        # Note: output can be either 1 (stage) or 2 (shield), and t is in kelvin
        if setpoint < self.t_switch:
            self.set_heater_range(1, "medium")
            self.set_heater_range(2, "medium")
        elif setpoint >= self.t_switch:
            self.set_heater_range(1, "high")
            self.set_heater_range(2, "high")
        self.visa.write(f"SETP {output},{setpoint}")
        time.sleep(self.wait)

    def read_filter(self, channel):
        # return samples, window
        val = self.visa.query(f"filter? {channel}").split(",")
        time.sleep(self.wait)
        return val

    def read_heater_range(self, channel):
        val = self.scpi_r["range"][self.visa.query(f"range? {channel}").strip("\n").strip("\r")]
        time.sleep(self.wait)
        return val

    def read_pid(self, pid):
        # return p, i , d
        val = [float(x) for x in self.visa.query(f"pid? {pid}").split(",")]
        time.sleep(self.wait)
        return val

    def read_model(self):
        # return model number
        val = self.visa.query("*IDN?").rstrip()
        time.sleep(self.wait)
        return val

    def read_temperature(self, sensor="all"):
        # read temperature from sensors ("all", "a", "b", "c" or "d")
        if sensor == "all":
            val = [float(x) for x in self.visa.query(f"KRDG? {self.scpi_w["sensor"][sensor]}").split(",")]
        else:
            val = float(self.visa.query(f"KRDG? {self.scpi_w["sensor"][sensor]}"))
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

    def configure(
            self,
            range_heater_1="high",
            range_heater_2="high",
            filter_state="on",
            filter_samples=64,
            filter_window=2,
            p1=75,
            i1=15,
            d1=0,
            p2=50,
            i2=20,
            d2=0
    ):
        self.set_filter("a", filter_state, filter_samples, filter_window)
        self.set_filter("b", filter_state, filter_samples, filter_window)
        self.set_filter("c", filter_state, filter_samples, filter_window)
        self.set_filter("d", filter_state, filter_samples, filter_window)
        self.set_heater_range(1, range_heater_1)
        self.set_heater_range(2, range_heater_2)
        self.set_pid(1, p1, i1, d1)
        self.set_pid(2, p2, i2, d2)

    def get_settings(self):
        return {
            "model": self.read_model(),
            "filter channel a (state, samples, window)": self.read_filter("a"),
            "filter channel b (state, samples, window)": self.read_filter("b"),
            "filter channel c (state, samples, window)": self.read_filter("c"),
            "filter channel d (state, samples, window)": self.read_filter("d"),
            "heater 1 range": self.read_heater_range(1),
            "heater 2 range": self.read_heater_range(1),
            "pid 1 settings (p, i, d)": self.read_pid(1),
            "pid 2 settings (p, i, d)": self.read_pid(2),
        }
