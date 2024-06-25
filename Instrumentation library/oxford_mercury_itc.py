import time
from collections import defaultdict


class mercuryitc():

    def __init__(self, visa, wait=0.01):

        self.visa = visa
        self.wait = wait
        self.visa.query("*RST")
        self.model = self.read_model()

    '''----- Set functions ------'''

    def set_temperature(self, output, setpoint):
        # Note: "output" can be either 0 (HeHigh or He3Pot) or 1 (He4Pot), and "setpoint" is in K
        if output == 0:
            val = self.visa.query("SET:DEV:DB7.T1:TEMP:LOOP:TSET:{}".format(setpoint))
        elif output == 1:
            val = self.visa.query("SET:DEV:DB6.T1:TEMP:LOOP:TSET:{}".format(setpoint))
        time.sleep(self.wait)
        return val

    def set_heater_percentage_auto(self, heater, value="ON"):
        # Note: heater can be either 1 (HeHigh or He3Pot) or 2 (He4Pot), and t is in kelvin
        if heater == 1:
            val = self.visa.query("SET:DEV:DB7.T1:TEMP:LOOP:ENAB:{}".format(value))
        elif heater == 2:
            val =self.visa.query("SET:DEV:DB6.T1:TEMP:LOOP:ENAB:{}".format(value))
        time.sleep(self.wait)
        time.sleep(5)
        return val

    '''----- Read functions ------'''

    def read_modules(self):
        val = self.visa.query("READ:SYS:CAT").split(".")
        time.sleep(self.wait)
        return val

    def read_model(self):
        val = self.visa.query("READ:SYS:MAN").strip("\n")
        time.sleep(self.wait)
        return val

    def read_temperature(self, sensor):
        # sensor can be either "a" (hehigh), "b" (he4pot), "c" (he3sorb) or "d" ("helow")
        if sensor == "c":
            val = float(self.visa.query("READ:DEV:MB1.T1:TEMP:SIG:TEMP").strip("\n").split(":")[-1][:-1])
        if sensor == "b":
            val = float(self.visa.query("READ:DEV:DB6.T1:TEMP:SIG:TEMP").strip("\n").split(":")[-1][:-1])
        if sensor == "a":
            val = float(self.visa.query("READ:DEV:DB7.T1:TEMP:SIG:TEMP").strip("\n").split(":")[-1][:-1])
        if sensor == "d":
            val = float(self.visa.query("READ:DEV:DB8.T1:TEMP:SIG:TEMP").strip("\n").split(":")[-1][:-1])
        time.sleep(self.wait)
        return val

    ''' ----- Operation functions ----- '''

    def clear_status(self):
        self.visa.write("*CLS")