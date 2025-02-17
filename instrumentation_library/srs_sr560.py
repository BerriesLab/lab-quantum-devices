class SR560:
    """ A class to control an SR560 Voltage pre-amplifier. """

    def __init__(
            self,
            address: str = None,
            gain: int = 1e3,
            lpf: float = 100,
            hpf: float = 0.0,
            coupling: str = "dc",
    ):
        self.address = address  # Set None if not connected to PC
        self.gain = gain  # Gain (in V/V)
        self.lpf = lpf  # Low pass filter cutoff frequency (in Hz)
        self.hpf = hpf  # High pass filter cutoff frequency (in Hz)
        self.coupling = coupling.lower()  # Coupling (ac or dc)
