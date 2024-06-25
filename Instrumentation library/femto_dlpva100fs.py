class dlpva100fs():

    # dlpva100fs is a single-ended amplifier. Careful when making differential measurements because the input signal is
    # amplified with respect to ground.

    # GAIN SETTING
    # GAIN  PIN 11  PIN 12
    # 20    LOW     LOW
    # 40    HIGH    LOW
    # 60    LOW     HIGH
    # 80    HIGH    HIGH

    # AC/DC SETTING
    # COUPLING  PIN 13
    # AC        LOW
    # DC        HIGH

    # BANDWIDTH SETTING
    # BANDWIDTH     PIN 14
    # 1kHz          LOW
    # 100 kHz       HIGH

    comm = {"gain": {1E1: "00", 1E2: "01", 1E3: "10", 1E4: "11"},
            "coupling": {"ac": "0", "dc": "1"},
            "bandwidth": {1E3: "0", 100E3: "1"}}

    def __init__(self, visa, dll, unit):

        self.visa = visa
        self.dll = dll
        self.unit = unit
        self.gain = None
        self.coupling = None
        self.bandwidth = None

    def init(self, gain, coupling, bandwidth):

        self.dll.EnumerateUsbDevices()
        self.error(self.dll.LedOn(self.unit))
        self.gain = gain
        self.coupling = coupling
        self.bandwidth = bandwidth
        self.write_settings()

    def write_settings(self):

        status = self.dll.WriteData(self.unit,
                                    int("{}{}{}".format(self.comm["bandwidth"][self.bandwidth],
                                                        self.comm["coupling"][self.coupling],
                                                        self.comm["gain"][self.gain] + "0")),
                                    0)

        self.error(status)

    def error(self, value):

        if value == -1:
            exit("Cannot find DLPVA {}".format(self.unit))

        if value == -2:
            exit("DLPVA {} does not respond".format(self.unit))

    def get_attributes(self):
        return [(x, self.__getattribute__(x)) for x in self.__dir__()][0:6]
