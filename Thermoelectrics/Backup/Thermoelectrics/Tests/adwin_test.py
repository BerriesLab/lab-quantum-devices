# region ----- Import packages -----
import adwin
from Objects.Backup.measurement_objects import *

# endregion

settings = EmptyClass()
settings.__setattr__("adc", EmptyClass())
settings.adc.model = 0                      # [int] select adc model (0: adwin gold ii)
settings.adc.input_resolution = 18          # [int] input resolution (in bit)
settings.adc.output_resolution = 16         # [int] output resolution (in bit)
settings.adc.clock_freq = 300e6             # [int] clock frequency (in Hz)
settings.adc.line_freq = 50                 # [int] line frequency (in Hz)
settings.adc.scanrate = 400e3               # [int] frequency at which the script is executed (in Hz)
settings.adc.nplc = 1                       # [float] number of power line cycles
settings.adc.sampling_freq = 10e3           # [int] sampling frequency (the number of samples internally averaged is: nplc / line_freq * sampling_freq)
settings.adc.iv_settling_time = 10e-3       # [float] settling time (in s) before recording data
settings.adc.vt_settling_time = 60 * 3      # [float] measurement time (in s). The number of samples is: vt_time / (nplc / line_freq)
settings.adc.vt_measurement_time = 60 * 1   # [float] measurement time (in s). The number of samples is: vt_time / (nplc / line_freq)

boot_dir = "C:/ADwin/ADwin11.btl"  # directory of boot file
routines_dir = "C:/Python scripts/lab-scripts/Instrumentation library/Adwin/Gold II"  # directory of routines files
adc = adwin.adwin(boot_dir, routines_dir)
adc.adw.Load_Process(routines_dir + "/sweep_2_ao_read_2_ai.TB1")
adc.adw.Set_Processdelay(1, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
adc.adw.Load_Process(routines_dir + "/read_8_ai_gold_ii.TB2")
adc.adw.Set_Processdelay(2, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))
adc.adw.Load_Process(routines_dir + "/sweep_2_ao.TB4")
adc.adw.Set_Processdelay(4, int(ceil(settings.adc.clock_freq / settings.adc.scanrate)))