import numpy as np


class PassiveVoltageDivider:
    """ A class to store the settings of a passive voltage divider. """

    def __init__(
            self,
            gain: float = 0.1,
            lpf: float = np.inf,
            hpf: float = 0.0
    ):
        self.gain = gain  # Gain (in V/V)
        self.lpf = lpf  # Low pass filter cutoff frequency (in Hz)
        self.hpf = hpf  # High pass filter cutoff frequency (in Hz)
