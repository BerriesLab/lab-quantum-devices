from Objects.measurement import EmptyClass
settings = EmptyClass()

# region ----- tc settings -----
settings.__setattr__("tc", EmptyClass())
settings.tc.model = 1                       # [int] select tc model (0: lakeshore 336, 1: oxford mercury itc)
settings.tc.address = "ASRL8::INSTR"        # [string] address of temperature controller
settings.tc.t_switch = 50                   # [float] temperature (in K) below which the Lakeshore 336 heater range is set to "medium"
settings.tc.sampling_freq = 1               # [int] temperature sampling frequency (in Hz)
settings.tc.settling_time = 0.01*15 * 60         # [float] cryostat thermalization time (in s).
settings.tc.settling_time_init = 0.01 * 15 * 60    # [float] cryostat initial thermalization time (in s).
settings.tc.settling_time_after_heater_sweep = settings.tc.settling_time  # [float] cryostat thermalization time (in s) after heater sweep.
# endregion

# region ----- adc settings -----
settings.__setattr__("adc", EmptyClass())
settings.adc.model = 0                      # [int] select adc model (0: adwin gold ii)
settings.adc.input_resolution = 18          # [int] input resolution (in bit)
settings.adc.output_resolution = 16         # [int] output resolution (in bit)
settings.adc.clock_freq = 300e6             # [int] clock frequency (in Hz)
settings.adc.line_freq = 50                 # [int] line frequency (in Hz)
settings.adc.scanrate = 40e3                # [int] frequency at which the script is executed (in Hz)
settings.adc.nplc = 10                      # [float] number of power line cycles
settings.adc.iv_settling_time = 0.01         # [float] I-V settling time (in s) before recording data
settings.adc.vt_settling_time = 0.1*60 * 5      # [float] V-t measurement settling time (in s). The number of samples is: vt_settling_time / (nplc / line_freq)
settings.adc.vt_measurement_time = 60 * 1   # [float] V-t measurement time (in s). The number of samples is: vt_measurement_time / (nplc / line_freq)
# endregion

# region ----- src1 settings -----
settings.__setattr__("src1", EmptyClass())
settings.src1.model = 1                     # [int] select src1 model (0: srs cs580, 1: tu delft IVa)
settings.src1.address = None                # [string] address. Set None if not connected to PC
settings.src1.gain = 100e-6                 # [float] gain (in A/V)
settings.src1.isolation = "float"           # [string] isolation
settings.src1.shield = "return"             # [string] shield
settings.src1.compliance = 1                # [float] compliance (in V)
settings.src1.response = None               # [string] response ("slow" adds a 470 pF to the output. The response time of the circuit is R * 470 pF)
settings.src1.delay = 0.1                   # [string] current source settling time (in s). Used when unit is controlled via Serial.
settings.src1.rate = 10e-6                  # [float] current sweep rate (in A/s). Used in current sweep when unit is controlled via Serial.
settings.src1.step = 1e-6                   # [float] current step (in A). Used in current sweep when unit is controlled via Serial.
# endregion

# region ----- src2 settings -----
settings.__setattr__("src2", EmptyClass())
settings.src2.model = settings.src1.model   # [int] select src1 model (0: srs cs580, 1: tu delft IVa)
settings.src2.address = None                # [string] address. Set None if not connected to PC
settings.src2.gain = settings.src1.gain     # [float] gain (in A/V)
settings.src2.isolation = settings.src1.isolation  # [string] isolation
settings.src2.shield = settings.src1.shield  # [string] shield
settings.src2.compliance = settings.src1.compliance  # [float] compliance (in V))
settings.src2.response = settings.src1.response  # [string] response ("slow" adds a 470 pF to the output. The response time of the circuit is R * 470 pF)
settings.src2.delay = settings.src1.delay   # [string] current source settling time (in s)
settings.src2.step = settings.src1.step     # [float] current step (in A). Used in current sweep.
# endregion

# region ----- src3 settings -----
settings.__setattr__("src3", EmptyClass())
settings.src3.model = 0                     # [int] select src1 model (0: srs cs580, 1: tu delft XXX)
settings.src3.address = "ASRL5::INSTR"     # [string] address. Set None if not connected to PC
settings.src3.gain = 10e-3                  # [float] gain (in A/V)
settings.src3.isolation = "float"           # [string] isolation
settings.src3.shield = "return"             # [string] shield
settings.src3.compliance = 7                # [float] compliance (in V)
settings.src3.response = "slow"             # [string] response
settings.src3.delay = 0.1                   # [string] current source settling time (in s). Used when unit is controlled via Serial.
settings.src3.rate = 10e-6                  # [float] current sweep rate (in A/s). Used in current sweep when unit is controlled via Serial.
settings.src3.step = 1e-6                   # [float] current step (in A). Used in current sweep when unit is controlled via Serial.
# endregion

# region ----- avv1 settings -----
settings.__setattr__("avv1", EmptyClass())
settings.avv1.model = 1                     # [int] select amplifier model (0: srs sr560, 1: tu delft IVa, 2: tu delft M2m)
settings.avv1.address = None                # [string] address. Set None if not connected to PC
settings.avv1.gain = 1e2                    # [float] gain (in V/V)
settings.avv1.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avv1.coupling = None               # [string] coupling (ac or dc)
# endregion

# region ----- avv2 settings -----
settings.__setattr__("avv2", EmptyClass())
settings.avv2.model = settings.avv1.model   # [int] select amplifier model (0: srs sr560, 1: tu delft M2m)
settings.avv2.address = settings.avv1.address  # [string] address. Set None if not connected to PC
settings.avv2.gain = settings.avv1.gain     # [float] gain (in V/V)
settings.avv2.lpf = settings.avv1.lpf       # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.hpf = settings.avv1.hpf       # [float] low pass filter cutoff frequency (in Hz)
settings.avv2.coupling = settings.avv1.coupling  # [string] coupling (ac or dc)
# endregion

# region ----- avi1 settings -----
settings.__setattr__("avi1", EmptyClass())
settings.avi1.model = 1                     # [int] select amplifier model (0: Femto ddpca-300, 1: stanford sr560)
settings.avi1.address = None                # [string] address. Set None if not connected to PC
settings.avi1.gain = 1e3 * 100e3            # [float] gain (in V/A). When the amplifier is V/V, the gain is "Gain*Resistance"
settings.avi1.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi1.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi1.coupling = "dc"               # [string] coupling (ac or dc)
# endregion

# region ----- avi2 settings -----
settings.__setattr__("avi1", EmptyClass())
settings.avi2.model = 1                     # [int] select amplifier model (0: Femto ddpca-300, 1: stanford sr560)
settings.avi2.address = None                # [string] address. Set None if not connected to PC
settings.avi2.gain = 1e3 * 100e3            # [float] gain (in V/A). When the amplifier is V/V, the gain is "Gain*Resistance"
settings.avi2.lpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi2.hpf = None                    # [float] low pass filter cutoff frequency (in Hz)
settings.avi2.coupling = "dc"               # [string] coupling (ac or dc)
# endregion

# region ----- lock-in1 settings -----
# When using external adc, Output = (signal/sensitivity - offset) x Expand x 10 V
# Set offset = 0 and Expand = 1 (default)
settings.__setattr__("lockin1", EmptyClass())
settings.lockin1.address = "GPIB0::1::INSTR"  # [string] address of lockin 1
settings.lockin1.reference = "internal"     # [string] reference source ("internal" or "external")
settings.lockin1.freq = 3.745               # [float] excitation current frequency (in Hz)
settings.lockin1.shield = "float"           # [string] shield ca nbe floating or shorted
settings.lockin1.coupling = "ac"            # [string] coupling can be AC (add a HPF at 0.16 Hz) or DC
settings.lockin1.time = 3                   # [float] integration time
settings.lockin1.filter = "24 dB/oct"       # [string] filter
settings.lockin1.input = "a"                # [string] input can be single ended ("a") or differential ("a-b")
settings.lockin1.sensitivity = 50e-3        # [string] sensitivity (in V). If input signal is current, sensitivity (in A) = sensitivity (in V) * 1e-6 A/V
settings.lockin1.harmonic = 2               # [int] demodulated harmonic
settings.lockin1.reserve = "normal"         # [string] reserve
# endregion

# region ----- lock-in2 settings -----
settings.__setattr__("lockin2", EmptyClass())
settings.lockin2.address = "GPIB0::2::INSTR"  # [string] address of lockin 2
settings.lockin2.reference = "external"     # [string] reference source ("internal" or "external")
settings.lockin2.freq = settings.lockin1.freq  # [float] excitation current frequency (in Hz)
settings.lockin2.shield = settings.lockin1.shield  # [string] shield ca nbe floating or shorted
settings.lockin2.coupling = settings.lockin1.coupling  # [string] coupling can be AC (add a HPF at 0.16 Hz) or DC
settings.lockin2.time = settings.lockin1.time  # [float] integration time
settings.lockin2.filter = settings.lockin1.filter  # [string] filter
settings.lockin2.input = settings.lockin1.input  # [string] input can be single ended ("a") or differential ("a-b")
settings.lockin2.sensitivity = settings.lockin1.sensitivity  # [string] sensitivity (in V). If input signal is current, sensitivity (in A) = sensitivity (in V) * 1e-6 A/V
settings.lockin2.harmonic = settings.lockin1.harmonic  # [int] demodulated harmonic
settings.lockin2.reserve = settings.lockin1.reserve  # [string] reserve
# endregion

# region ----- lock-in3 settings -----
# When using external adc, Output = (signal/sensitivity - offset) x Expand x 10 V
# Set offset = 0 and Expand = 1 (default)
settings.__setattr__("lockin3", EmptyClass())
settings.lockin3.address = "GPIB0::1::INSTR"  # [string] address of lockin 1
settings.lockin3.reference = "internal"     # [string] reference source ("internal" or "external")
settings.lockin3.freq = 3.745               # [float] excitation current frequency (in Hz)
settings.lockin3.shield = "float"           # [string] shield ca nbe floating or shorted
settings.lockin3.coupling = "ac"            # [string] coupling can be AC (add a HPF at 0.16 Hz) or DC
settings.lockin3.time = 3                   # [float] integration time
settings.lockin3.filter = "24 dB/oct"       # [string] filter
settings.lockin3.input = "a"                # [string] input can be single ended ("a") or differential ("a-b")
settings.lockin3.sensitivity = 50e-3        # [string] sensitivity (in V). If input signal is current, sensitivity (in A) = sensitivity (in V) * 1e-6 A/V
settings.lockin3.harmonic = 2               # [int] demodulated harmonic
settings.lockin3.reserve = "normal"         # [string] reserve
# endregion
