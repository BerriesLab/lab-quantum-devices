import numpy as np
import time
from collections import defaultdict


class dmm2182a():

    '''----- Initialize object -----'''

    def __init__(self, visa, wait=0.01):

        self.visa = visa
        self.wait = wait
        self.model = self.read_model()

        # Restore factory defaults of smu
        self.visa.write(":syst:pres")
        self.visa.write("*rst")
        # Clears all event registers and Error Queue
        self.clear_measurement_event_register()



    '''----- Set settings functions -----'''

    def set_function(self, function="'voltage'"):
        # 'voltage' or 'temperature', apex necessary
        self.visa.write(":sense:function {}".format(function))
        time.sleep(self.wait)

    def set_channel(self, channel=1):
        # Select channel to measure; 0, 1 or 2 (0 = internal temperature sensor).
        self.visa.write(":sense:channel {}".format(channel))
        time.sleep(self.wait)

    def set_range(self, channel=1, sense_range=0.1):
        # Range is the expected reading: 0 to 120 (volts). The 2182a sets the range accordingly to measure the value
        self.visa.write(":sense:voltage:channel{}:range:upper {}".format(channel, sense_range))
        time.sleep(self.wait)

    def set_autorange(self, channel=1, state="on"):
        self.visa.write(":sense:voltage:channel{}:range:auto {}".format(channel, state))
        time.sleep(self.wait)

    def set_nplc(self, function="voltage", nplc=1):
        self.visa.write(":sense:{}:nplcycles {}".format(function, nplc))
        time.sleep(self.wait)

    def set_digits(self, function="voltage", digits=8):
        self.visa.write(":sense:{}:digits {}".format(function, digits))
        time.sleep(self.wait)

    def set_lpf(self, function="voltage", state="on"):
        self.visa.write(":sense:{}:lpass:state {}".format(function, state))
        time.sleep(self.wait)

    def set_filter_state(self, function="voltage", state="on"):
        self.visa.write(":sense:{}:dfilter:state {}".format(function, state))
        time.sleep(self.wait)

    def set_filter_count(self, function="voltage", n=1):
        # n from 1 to 100
        self.visa.write(":sense:{}:dfilter:count {}".format(function, n))
        time.sleep(self.wait)

    def set_filter_control(self, function="voltage", control="repeat"):
        # moving or repeat
        self.visa.write(":sense:{}:dfilter:tcontrol {}".format(function, control))
        time.sleep(self.wait)

    # def set_filter_window(self, function="voltage", window=10):
    #     self.visa.write(":sense:{}:dfilter:window {}".format(function, window))

    def set_trigger_source(self, source="bus"):
        self.visa.write(":trigger:source {}".format(source))
        time.sleep(self.wait)

    def set_trigger_delay(self, delay="default"):
        # delay in seconds from 0 to 999999.99, or default = 100 ms
        self.visa.write(":trigger:delay {}".format(delay))
        time.sleep(self.wait)

    def set_trigger_autodelay(self, state="on"):
        self.visa.write(":trigger:delay:auto {}".format(state))
        time.sleep(self.wait)

    def set_trigger_count(self, n="inf"):
        # from 1 to 9999 or infinite
        self.visa.write(":trigger:count {}".format(n))
        time.sleep(self.wait)

    def set_sample_count(self, n=1):
        self.visa.write(":sample:count {}".format(n))
        time.sleep(self.wait)

    def set_initiate_continuous(self, state="on"):
        self.visa.write(":initiate:continuous {}".format(state))
        time.sleep(self.wait)

    def set_status_measurement_register(self, status=32):
        # Bit B5 (32), Reading Available (RAV) - Set bit indicates that a reading was taken and processed.
        # Bit B7 (128), Buffer Available (BAV) - Set bit indicates that there are at least two readings in the trace buffer.
        # Bit B8 (256), Buffer Half Full (BHF) - Set bit indicates that the trace buffer is half full.
        # Bit B9 (512), Buffer Full (BFL) - Set bit indicates that the trace buffer is full.
        self.visa.write(":status:measurement:enable {}".format(status))
        time.sleep(self.wait)

    def set_sre_register(self, status=1):
        # 0 Clears enable register
        # 1 Set MSB bit (Bit 0) - status measurement register summary bit
        # 4 Set EAV bit (Bit 2)
        # 8 Set QSB bit (Bit 3)
        # 16 Set MAV bit (Bit 4)
        # 32 Set ESB (Bit 5)
        # 128 Set OSB (Bit 7)
        # 255 Set all bits
        self.visa.write("*sre {}".format(status))
        time.sleep(self.wait)

    def set_line_sync(self, state="off"):
        self.visa.write(":system:lsync {}".format(state))
        time.sleep(self.wait)

    '''----- Read function -----'''

    def read_function(self):
        val = self.visa.query(":sense:function?").strip("\n").lower()
        time.sleep(self.wait)
        return val

    def read_channel(self):
        val = self.visa.query(":sense:channel?").strip("\n")
        time.sleep(self.wait)
        return val

    def read_range(self, channel=1):
        val = self.visa.query(":sense:voltage:channel{}:range?".format(channel)).strip("\n")
        time.sleep(self.wait)
        return val

    def read_autorange(self, channel=1):
        val = self.visa.query(":sense:voltage:channel{}:range:auto?".format(channel)).strip("\n")
        time.sleep(self.wait)
        return val

    def read_nplc(self, function="voltage"):
        val = self.visa.query(":sense:{}:nplc?".format(function)).strip("\n")
        time.sleep(self.wait)
        return val

    def read_digits(self, function="voltage"):
        val = self.visa.query(":sense:{}:digits?".format(function)).strip("\n")
        time.sleep(self.wait)
        return val

    def read_lpf(self, function="voltage"):
        val = self.visa.query(":sense:{}:lpass:state?".format(function)).strip("\n")
        time.sleep(self.wait)
        if val == "1":
            return "on"
        if val == "0":
            return "off"

    def read_filter_state(self, function="voltage"):
        val = self.visa.query(":sense:{}:dfilter:state?".format(function)).strip("\n")
        time.sleep(self.wait)
        if val == "1":
            return "on"
        if val == "0":
            return "off"

    def read_filter_control(self, function="voltage"):
        val = self.visa.query(":sense:{}:dfilter:tcontrol?".format(function)).lower().strip("\n")
        time.sleep(self.wait)
        if val == "rep":
            return "repeat"
        if val == "mov":
            return "moving"

    def read_filter_count(self, function="voltage"):
        val = int(self.visa.query(":sense:{}:dfilter:count?".format(function)).strip("\n"))
        time.sleep(self.wait)
        return val

    def read_filter_window(self, function="voltage"):
        val = self.visa.query(":sense:{}:dfilter:window?".format(function)).strip("\n")
        time.sleep(self.wait)
        return val

    def read_trigger_source(self):
        val = self.visa.query(":trigger:source?").lower().strip("\n")
        time.sleep(self.wait)
        return val

    def read_trigger_count(self):
        val = float(self.visa.query(":trigger:count?").strip("\n"))
        time.sleep(self.wait)
        if val > 9999:
            return "infinite"
        else:
            return val

    def read_initiate_continuous(self):
        val = self.visa.query(":initiate:continuous?").lower().strip("\n")
        time.sleep(self.wait)
        if val == "1":
            return "on"
        if val == "0":
            return "off"

    def read_status_measurement_register(self):
        val = self.visa.query(":status:measurement:enable?").lower().strip("\n")
        time.sleep(self.wait)
        return val

    def read_model(self):
        val = self.visa.query("*idn?").strip("\n").lower()
        time.sleep(self.wait)
        return val

    def read_sre_register(self):
        val = self.visa.query("*sre?").strip("\n")
        time.sleep(self.wait)
        return val

    '''----- Operation function -----'''

    def initiate(self):
        self.visa.write(":initiate:immediate")
        time.sleep(self.wait)

    def clear_srq_enable_register(self):
        self.visa.write("*sre 0")
        time.sleep(self.wait)

    def clear_measurement_event_register(self):
        self.visa.write("*cls")
        time.sleep(self.wait)

    def read_new(self):
        val = self.visa.query(":sense:data:fresh?")
        return val

    def read_last(self):
        val = float(self.visa.query(":sense:data:latest?"))
        return val

    def configure(self, lpf="on", samples=1, sense_range=10e-3, nplc=1, trigger_source="bus", trigger_count="inf", trigger_delay="default",
                     trigger_autodelay_state="on", autorange="off"):
        # program measurement. A trigger is needed to initiate the measurement
        self.set_initiate_continuous("off")
        self.set_function()
        self.set_channel()
        self.set_nplc(nplc=nplc)
        self.set_digits()
        self.set_range(sense_range=sense_range)
        self.set_autorange(state=autorange)
        # configure analog and digital filter
        self.set_lpf(state=lpf)
        self.set_filter_state(state="on")
        self.set_filter_count(n=samples)
        # # self.set_filter_window()
        self.set_filter_control()
        self.set_line_sync()
        # # configure trigger
        self.set_sample_count(n=1)
        self.set_trigger_source(source=trigger_source)
        self.set_trigger_count(n=trigger_count)
        self.set_trigger_delay(delay=trigger_delay)
        self.set_trigger_autodelay(state=trigger_autodelay_state)
        # configure measurement status register and service request enable register to raise a request upon measurement completion
        self.set_sre_register(1)
        self.set_status_measurement_register(32)
        self.visa.write("*wai")
        self.initiate()

    def read(self, lpf="on", samples=1, sense_range=10e-3, nplc=1, trigger_source="bus", trigger_count="inf", trigger_delay="default",
             trigger_autodelay_state="on"):
        # program measurement. A trigger is needed to initiate the measurement
        self.configure(lpf, samples, sense_range, nplc, trigger_source, trigger_count, trigger_delay, trigger_autodelay_state)
        self.send_trigger()
        self.wait_for_srq()
        return self.read_last()

    def send_trigger(self):
        self.visa.write("*trg")

    def wait_for_srq(self, timeout=None):
        self.visa.wait_for_srq(timeout=timeout)

    def stop(self):
        self.visa.write("abort")

    def get_settings(self):
        return {"dmm unit": self.read_model(),
                "autorange": self.read_autorange(),
                "range": self.read_range(),
                "nplc": self.read_nplc(),
                "low pass filter": self.read_lpf(),
                "digital filter": self.read_filter_state(),
                "digital samples": self.read_filter_count()
                }

