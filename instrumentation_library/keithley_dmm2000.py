import numpy as np
import time
from collections import defaultdict


class dmm2000():

    # dictionary for SCPI communication
    scpi_w = {"filter_status": {"off": "0", "on": "1"}, "filter_type": {"moving": "mov", "repeat": "rep"}}

    # SCPI dictionary for reading from instrumentation
    scpi_r = defaultdict(dict)
    for key, val in scpi_w.items():
        for subkey, subval in val.items():
            scpi_r[key][subval] = subkey

    def __init__(self, visa):
        # create a local registry
        self.visa = visa
        self.model = self.read_model()

        # reset the dmm to default settings
        self.visa.write("*rst")

        # clears the following enable registers: Operation Event Enable Register, Questionable Event Enable Register,
        # and measurement Event Enable Register
        self.visa.write("status:preset")

        # clear all event registers (to prevent previous operations to interfere with the current measurements)
        self.visa.write("*cls")

        # put the dmm in idle state (waiting for a trigger)
        self.visa.write(":initiate:continuous off")

        # clear buffer
        self.visa.write("trace:clear")

    def set_status_register(self, register):
        # enable the measurement status register BFL (buffer full). Note: The sum of the decimal weights of the bits that you wish
        # to set is sent as the parameter (<NRf>) for the appropriate :ENABle command. For example, to set the BFL and RAV bits
        # of the measurement Event Enable Register, send the following command:stat:meas:enab 544 where BFL (bit B9) = Decimal = 512
        # and RAV (bit B5) = Decimal = 32, so that <NRf> = 512 + 32 = 544
        # *sre 1 activate the MSB enable register (BFL and RAV belong to MSB register)
        self.visa.write("status:measurement:enable {}; *sre 1".format(register))

    def set_sense_function(self, function="dc:volt"):
        # set sense to voltage dc. # Note: the apexes '' are required
        self.visa.write("sense:function '{}'".format(function))

    def set_digits(self, digits, sense_function):
        # set resolution to seven digits (affects the display only)
        self.visa.write("sense:{}:digits {}".format(sense_function, digits))

    def set_sense_range(self, sense_range, sense_function):
        # set the range between 0.1, 1, 10, 100 volts
        self.visa.write("sense:{}:range {}".format(sense_function, sense_range))

    def set_nplc(self, nplc, sense_function):
        # set number of n_plc between 0.01 (200 us) and 10 (200 ms)
        self.visa.write("sense:{}:nplcycles {}".format(sense_function, nplc))

    def set_filter_state(self, state, sense_function):
        # enable (1)/disable (0) digital filter
        self.visa.write("sense:{}:average:state {}".format(sense_function, self.scpi_w["filter_status"][state]))

    def set_filter_type(self, type, sense_function):
        # set digital filter to moving (MOV)/ repeat REP). Note: if the repeat filter is enabled, then the instrument samples the
        # specified number of reading conversions to yield a single filtered reading. If the moving filter is active, or filter is
        # disabled, then only one reading conversion is performed.
        self.visa.write("sense:{}:average:tcontrol {}".format(sense_function, self.scpi_w["filter_type"][type]))

    def set_filter_samples(self, n, sense_function):
        # set number of digital samples to average between 1 and 100
        # Note: each measurement will take the time 20 ms * NPLC * filter samples
        self.visa.write("sense:{}:average:count {}".format(sense_function, n))

    def set_bandwidth(self, bandwidth):
        # set the bandwidth of the dmm
        sense = self.read_sense_function()
        self.visa.write("sense:{}:detector:bandwidth {}".format(sense, bandwidth))

    def set_trigger_count(self, n):
        # set the number of trigger events expected by the dmm before going back to idle.
        # Note: in order to prevent the dmm to go into idle, set count to "infinity"
        self.visa.write("trigger:count {}".format(n))

    def set_trigger_source(self, source):
        # set control source to IMMediate/TIMer/MANual/BUS/EXTernal.
        # Note: to send a trigger via software, set the trigger source to bus and use the command *TRG or GET to send the trigger
        self.visa.write("trigger:source {}".format(source))

    def set_trigger_delay_auto(self, auto):
        # set trigger delay auto to ON or OFF
        self.visa.write("trigger:delay:auto {}".format(auto))

    def set_sample_count(self, n):
        # set the number of samples between 1 and 1024 to acquire before the next trigger
        # event. Note: if sample count is > 1 then acquisition should be saved in the buffer and recalled by reading the buffer
        self.visa.write("sample:count {}".format(n))

    def set_buffer_size(self, n):
        # set the maximum number of data points to store in buffer between 2 and 1024
        self.visa.write("trace:points {}".format(n))

    '''----- Read functions -----'''

    def read_status_register(self):
        # read the enabled status register
        return self.visa.query("status:measurement:enable?").strip("\n")

    def read_sense_function(self):
        # read voltage dc. # Note: the apexes '' are required
        return self.visa.query("sense:function?").strip("\n").lower().strip('"')

    def read_digits(self, sense_function):
        # read display resolution
        return self.visa.query("sense:{}:digits?".format(sense_function)).strip("\n")

    def read_sense_range(self, sense_function):
        # read the sense range
        return self.visa.query("sense:{}:range?".format(sense_function)).strip("\n")

    def read_nplc(self, sense_function):
        # read number of n_plc
        return self.visa.query("sense:{}:nplcycles?".format(sense_function)).strip("\n")

    def read_filter_status(self, sense_function):
        # read digital filter status
        return self.scpi_r["filter_status"][self.visa.query("sense:{}:average:state?".format(sense_function)).strip("\n")]

    def read_filter_type(self, sense_function):
        # read digital filter type
        return self.scpi_r["filter_type"][self.visa.query("sense:{}:average:tcontrol?".format(sense_function)).lower().strip("\n")]

    def read_filter_samples(self, sense_function):
        # read number of digital samples averaged
        return self.visa.query("sense:{}:average:count?".format(sense_function)).strip("\n")

    def read_bandwidth(self, sense_function):
        # read dmm bandwidth
        return self.visa.query("sense:{}:detector:bandwidth?".format(sense_function)).strip("\n")

    def read_trigger_count(self):
        # read the number of trigger events expected by the dmm before going back to idle.
        return self.visa.query("trigger:count?").strip("\n")

    def read_trigger_source(self):
        # read trigger control source
        return self.visa.query("trigger:source?").lower().strip("\n")

    def read_trigger_delay_auto(self):
        # set trigger delay auto to ON or OFF
        return self.visa.query("trigger:delay:auto?").strip("\n")

    def read_sample_count(self):
        # read the number of samples to acquire before the next trigger
        return self.visa.query("sample:count?").strip("\n")

    def read_buffer_size(self):
        # read the maximum number of data points that can be stored in buffer
        return self.visa.query("trace:points?").strip("\n")

    '''----- Operation functions -----'''

    def abort(self):
        # put dmm into idle
        self.visa.write("abort")

    def get_offset(self):
        # return the offset
        return self.visa.write("acquire..")

    def start(self):
        # start measurement but do not wait for service request. It allows to run other processes in parallel.
        # Note: "iniitate" take the dm out of idle and make it ready to receive a trigger event
        self.visa.write("initiate")
        self.visa.write("*trg")  # send trigger over the bus

    def read(self):
        # perform :abort, :initiate and :fetch. Cannot be used if sample count is > 1
        return float(self.visa.query("sense:data?"))
        # return dmm.query("fetch?")

    def read_buffer(self):
        # return all data stored in buffer
        return np.array(self.visa.query_ascii_values("trace:data?"))

    def read_model(self):
        # returns the manufacturer, model number, serial number and firmware revision levels of the unit
        return self.visa.query("*idn?")

    def wait_for_srq(self):
        # wait for unit to raise a service request
        self.visa.wait_for_srq()

    def clear_event_register(self):
        self.visa.write("*cls")

    def get_settings(self):
        return {"dmm unit": self.read_model(),
                "sense function": self.read_sense_function(),
                "sense range": self.read_sense_range(self.read_sense_function()),
                "n_plc": self.read_nplc(self.read_sense_function()),
                "filter status": self.read_filter_status(self.read_sense_function()),
                "filter type": self.read_filter_type(self.read_sense_function()),
                "filter samples": self.read_filter_samples(self.read_sense_function())}

    def program_measure_on_trigger(self, sense_function="voltage:dc", sense_range=0.1, nplc=1, filter_state="off", filter_type="moving", filter_samples=1,
                                   trigger_source="bus", trigger_count="infinity", trigger_delay_auto="on", sample_count=1, buffer_size=1024, digits=7,
                                   status_register=512, bandwidth=300E3):
        #
        self.set_sense_function(sense_function)
        self.set_sense_range(sense_range, sense_function)
        self.set_nplc(nplc, sense_function)
        self.set_filter_state(filter_state, sense_function)
        self.set_filter_type(filter_type, sense_function)
        self.set_filter_samples(filter_samples, sense_function)
        self.set_trigger_source(trigger_source)
        self.set_trigger_count(trigger_count)
        self.set_trigger_delay_auto(trigger_delay_auto)
        self.set_sample_count(sample_count)
        self.set_buffer_size(buffer_size)
        self.set_digits(digits, sense_function)
        self.set_status_register(status_register)

        # set the source of data saved in buffer as "sense" (measured) data. Other option would be "calculate"
        self.visa.write("trace:feed sense1")

        # start filling the buffer upon receiving the trigger input.
        self.visa.write("trace:feed:control next")