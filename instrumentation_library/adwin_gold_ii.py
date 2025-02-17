from numpy import zeros, array, ndarray, ceil
import time
import ADwin


class ADwinGoldII:
    """ A class to control an ADwin Gold II. """

    def __init__(
            self,
            adwin_boot_dir: str = None,
            adwin_routines_dir: str = None,
            input_resolution: int = 18,
            output_resolution: int = 16,
            clock_freq: int = 300e6,
            line_freq: int = 50,
            scan_rate: int = 100e3,
            n_plc: float = 1.0,
            iv_settling_time: float = 0.0,
            vt_settling_time: float = 0.0,
            vt_measurement_time: float = 1.0,
            sweep_step: float = 0.01,
            process: list[str] = None,
    ):
        self.adw = ADwin.ADwin(0x1, 1)
        self.adwin_boot_dir = adwin_boot_dir  # Directory including ADwin Boot Files
        self.adwin_routines_dir = adwin_routines_dir  # Directory including ADwin Routine Files

        self.input_resolution = input_resolution  # [int] input resolution (in bit)
        self.output_resolution = output_resolution  # [int] output resolution (in bit)
        self.clock_freq = clock_freq  # [int] clock frequency (in Hz)
        self.line_freq = line_freq  # [int] line frequency (in Hz)
        self.scan_rate = scan_rate  # [int] frequency at which the script is executed (in Hz)
        self.n_plc = n_plc  # [float] number of power line cycles
        self.iv_settling_time = iv_settling_time  # [float] measurement time (in s). The number of samples is: vt_time / (n_plc / line_freq)
        self.vt_settling_time = vt_settling_time  # [float] measurement time (in s). The number of samples is: vt_time / (n_plc / line_freq)
        self.vt_measurement_time = vt_measurement_time  # [float] measurement time (in s). The number of samples is: vt_time / (n_plc / line_freq)
        self.sweep_step = sweep_step  # [float] voltage sweep step (in V)
        self.delay = 1
        self.process = process

        # Boot ADwin Gold II
        self.adw.Boot(self.adwin_boot_dir)
        if self.adw.Test_Version() == 0:
            print("Found ADwin Gold II.")
        else:
            raise ADwin.ADwinError("Cannot find ADwin Gold II.")

        # Configure ADwin Gold II
        self.configure()

    def configure(self):
        """ Configure ADwin. """
        for i in range(0, len(self.process)):
            self.load_process(self.process[i])
            self.set_process_delay(i + 1)
        self.set_number_of_readings_per_sample()
        self.set_output_settling_time()
        self.set_number_of_samples_to_read()
        self.set_ao_to_zero(ao=1)
        self.set_ao_to_zero(ao=2)

    def set_process_delay(self, process_n):
        """ Set 'process_number' delay in seconds. """
        self.adw.Set_Processdelay(process_n, int(ceil(self.clock_freq / self.scan_rate)))

    def set_number_of_readings_per_sample(self):
        """ N. samples to average in hardware = n_plc / line freq * scan_rate """
        n_samples = int(ceil(self.n_plc / self.line_freq * self.scan_rate))
        self.adw.Set_Par(33, n_samples)

    def set_output_settling_time(self):
        """ Settling time: no. of loops to wait after setting the output. """
        n_loops = int(ceil(self.iv_settling_time * self.scan_rate))
        self.adw.Set_Par(34, n_loops)

    def set_number_of_samples_to_read(self):
        """ N. samples = measurement_time / n_plc * line_freq"""
        n_samples = int(ceil(self.vt_settling_time + self.vt_measurement_time) / (self.n_plc / self.line_freq))
        self.adw.Set_Par(71, n_samples)

    def set_ao_to_zero(self, ao: int = 1):
        # set initial values of AO1 and AO2
        if ao not in [1, 2]:
            raise ADwin.ADwinError("Analog Output does not exist.")
        if ao == 1:
            self.adw.Set_Par(51, self.voltage2bin(0, bits=self.output_resolution))
        if ao == 2:
            self.adw.Set_Par(52, self.voltage2bin(0, bits=self.output_resolution))

    def start_process(self, process_number):
        """ Start 'process_number'. The process number starts from 1. """
        if not isinstance(process_number, int):
            raise ADwin.ADwinError("Process number must be type integer.")
        self.adw.Start_Process(process_number)

    def process_status(self, process_number):
        """ Check processes status of process number 'process_number'. """
        status = self.adw.Process_Status(process_number)
        if status == 0:
            return False
        elif status == 1:
            return True

    def load_process(self, process):
        """ Load process into ADwin. """
        self.adw.Load_Process(f"{self.adwin_routines_dir}/{process}")

    def get_par(self, number):
        if isinstance(number, int):
            val = self.adw.Get_Par(number)
            time.sleep(self.delay)
            return val

    def get_data(self, data_number, start_index, count):
        """ Get data from ADwin. """
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

    def make_iv(self, v, points2average):
        """Make iv: sweep AO1 and read AI1. """
        # Validate input
        if not isinstance(v, list):
            raise ValueError("v must be a list of voltage values, in Volt.")

        self.adw.Load_Process(f"{self.adwin_routines_dir}/sweep_ao1_read_ai1.TB1")
        time.sleep(self.delay)

        bin = self.voltage2bin(v)

        self.adw.SetData_Long(list(bin), 1, 1, len(bin))  # len(bin) if isinstance(bin, ndarray) else 1)
        self.set_process_delay(1)
        self.set_number_of_readings_per_sample()
        self.set_output_settling_time()
        self.adw.Set_Par(23, len(v))                # length of the voltage array

        self.adw.Set_Par(8, int(output_channel))  # set output
        self.adw.Set_Par(10, 18)  # set ADC input resolution

        self.adw.Start_Process(1)                   # run process
        while self.adw.Process_Status(1) == 1:
            pass

        data1 = self.adw.GetData_Float(2, 1, len(v))     # get averaged MUX1 current values
        # data5 = self.adw.GetData_Float(5, len(v))     # get averaged MUX2 current values
        return array(data1)

    def sweep_ao(self, process_number, v, output_channel, process_delay, settling_time, points2average):
        """ Sweep Analog Output """
        raise ADwin.ADwinError("Process not yet implemented")

    def record_ai(self, input_channel, process_delay, settling_time, points2average):
        """ Read analog input"""
        raise ADwin.ADwinError("Process not yet implemented")

    def read_buffer(self, buffer_number):
        """ Read data stored in ADwinGoldII buffer """
        raise ADwin.ADwinError("Process not yet implemented")
