from numpy import zeros, array, ndarray, log10
import ADwin
import time
import ctypes


class adwin():

    def __init__(self, adwin_boot_dir, adwin_routines_dir):
        """Wrapper around the object ADwin.ADwin. Includes methods to make experiments
        and to convert data."""

        self.adw = ADwin.ADwin(0x1, 1)
        self.adwin_routines_dir = adwin_routines_dir
        self.adwin_boot_dir = adwin_boot_dir
        self.delay = 1
        self.adw.Boot(self.adwin_boot_dir)  # Boot ADwin

        if self.adw.Test_Version() == 0:
            print("Found ADwin Gold II.")
        else:
            exit("Cannot find ADwin Gold II.")

    def get_par(self, number):
        if isinstance(number, int):
            val = self.adw.Get_Par(number)
            time.sleep(self.delay)
            return val

    def start_process(self, process_number):
        """ Start process number 'process_number'. The process number starts from 1. """
        if not isinstance(process_number, int):
            exit("Process number must be type integer.")
        self.adw.Start_Process(process_number)                   # run process

    def process_status(self, process_number):
        """ Check processes status of process number 'process_number'. """
        status = self.adw.Process_Status(process_number)
        if status == 0:
            return False
        elif status == 1:
            return True

    def load_process(self, process):
        """ Load porcess in ADwin. """
        self.adw.Load_Process(self.adwin_routines_dir + "/" + process)

    def get_data(self, data_number, start_index, count):
        return self.adw.GetData_Float(data_number, start_index, count)

    def voltage2bin(self, v, v_ref=-10, v_range=9.99969-(-10), bits=16):
        """Convert a scalar or array of voltages into bins"""
        if isinstance(v, ndarray):
            bins = zeros(len(v), dtype=int)
            for idx in range(len(v)):
                bins[idx] = self.voltage2bin(v[idx], v_ref, v_range, bits)
            return array(bins, dtype=int)
        else:
            return int((v - v_ref) / v_range * 2**bits)

    def bin2voltage(self, bin, v_ref=-10, v_range=9.99969-(-10), bits=16):
        """Convert a scalar or array of bins into voltage values"""
        if isinstance(bin, ndarray):
            v = zeros(len(bin), dtype=float)
            for idx in range(len(bin)):
                v[idx] = self.bin2voltage(bin[idx], v_ref, v_range, bits)
            return v
        else:
            return v_ref + bin * v_range / 2**bits

    def make_iv_ao1(self, v, output_channel, input_channel, process_delay, settling_time, points2average):
        """Make iv: sweep Analog Output(s) and record Analog Input(s).
        Channels 1-2, 3-4, 5-6, 7-8 are recorded simultaneously."""

        # select process to load depending on the number of output and input channels
        if isinstance(output_channel, int):
            if isinstance(input_channel, int):
                exit("ADwin script not implemented.")
            if isinstance(input_channel, list):
                self.adw.Load_Process(self.adwin_routines_dir + "\\" + "XXX.TB1")
        if isinstance(output_channel, list):
            if isinstance(input_channel, int):
                exit("ADwin script not implemented.")
            if isinstance(input_channel, list):
                self.adw.Load_Process(self.adwin_routines_dir + "\\" + "Sweep_AO_read_AI_single_GoldII.TB1")

        time.sleep(self.delay)

        bin = self.voltage2bin(v)

        self.adw.SetData_Long(list(bin), 1, 1, len(bin))  #len(bin) if isinstance(bin, ndarray) else 1)
        self.adw.Set_Processdelay(1, int(process_delay))  # frequency (300 MHz) / scanrate
        self.adw.Set_Par(21, int(points2average))        # n. of points to average (set a multiple of the line)
        self.adw.Set_Par(22, int(settling_time))         # settling time (n. of loops)
        self.adw.Set_Par(23, len(v))                # length of the voltage array

        self.adw.Set_Par(8, int(output_channel))  # set output
        self.adw.Set_Par(10, 18)  # set ADC input resilution

        self.adw.Start_Process(1)                   # run process
        while self.adw.Process_Status(1) == 1:
            pass

        data1 = self.adw.GetData_Float(2, 1, len(v))     # get averaged MUX1 current values
        # data5 = self.adw.GetData_Float(5, len(v))     # get averaged MUX2 current values
        return array(data1)

    def sweep_ao(self, process_number, v, output_channel, process_delay, settling_time, points2average):
        """ Sweep Analog Output """
        self.adw.Load_Process(self.adwin_routines_dir + "\\" + "Sweep_AO_read_AI_single_GoldII.TB1")
        time.sleep(self.delay)

    def record_ai(self, input_channel, process_delay, settling_time, points2average):
        """ Read analog input"""
        True

    def read_buffer(self, buffer_number):
        """ Read data stored in adwin buffer """
        True