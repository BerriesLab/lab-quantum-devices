class ddpca300():

    # Remote control input bits are opto-isolated. For remote
    # control operation set the rotary gain switch to the
    # “Remote” position and select the desired gain setting via a
    # bit code at the digital inputs.

    # GAIN SETTING
    # GAIN  PIN 13  PIN 12  PIN 11  PIN 10
    # 1E4   LOW     LOW     LOW     LOW
    # 1E5   LOW     LOW     LOW     HIGH
    # 1E6   LOW     LOW     HIGH    LOW
    # 1E7   LOW     LOW     HIGH    HIGH
    # 1E8   LOW     HIGH    LOW     LOW
    # 1E9   LOW     HIGH    LOW     HIGH
    # 1E10  LOW     HIGH    HIGH    LOW
    # 1E11  LOW     HIGH    HIGH    HIGH
    # 1E12  HIGH    LOW     LOW     LOW
    # 1E13  HIGH    LOW     LOW     HIGH

    # Switch settings “0.1 Hz / Full BW / 0.7 Hz” and
    # “Bias Ext. / Off / Int.” are not remote controllable.

    comm = {"gain": {1E4: "0000", 1E5: "0001", 1E6: "0010", 1E7: "0011", 1E8: "0100",
            1E9: "0101", 1E10: "0110", 1E11: "0111", 1E12: "1000", 1E13: "1001"}}

    def __init__(self, visa, unit, dll):

        self.visa = visa
        self.dll = dll
        self.unit = unit
        self.gain = None

        # self.read_settings(settings="all")

    def init(self, gain):

        self.dll.EnumerateUsbDevices()
        self.error(self.dll.LedOn(self.unit))
        self.gain = gain
        self.write_settings()

    def write_settings(self):

        status = self.dll.WriteData(self.unit, format(int("0000" + self.comm["gain"][self.gain], base=2), "#010b"), 0b00000000)
        self.error(status)

    def error(self, value):

        if value == -1:
            exit("Cannot find DLPVA {}".format(self.unit))

        if value == -2:
            exit("DLPVA {} does not respond".format(self.unit))

    def get_attributes(self):
        return [(x, self.__getattribute__(x)) for x in self.__dir__()][0:4]