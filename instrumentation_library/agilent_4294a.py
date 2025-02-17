import numpy as np

class agilent4294a():

    # dictonary
    a4294 = {"dc_range": {1e-3: "M1", 10e-3: "M10", 100e-3: "M100"}}

    def __init__(self, visa):
        self.visa = visa
        self.visa.write("*CLS")       # clear all
        self.visa.write("*RST")       # preset (sweep mode is set to HOLD)
        #self.visa.write("PRES")        # preset (does not reset instrument BASIC)
        self.visa.write("HOLD")         # hold the trigger (IDLE state)
        self.visa.write("FORM4")      # format ascii
        self.visa.write("TRGS INT")   # selects trigger source
        self.visa.write("E4TP OFF")  # adapter type NONE (E4TP M1: 1m extension, E4TP M2: 2m extension)
        #self.visa.write("CALST OFF")  # turns off the user calibration function
        #self.visa.write("COMSTA OFF")  # turn off OPEN compensation
        #self.visa.write("COMSTB OFF")  # turn off SHORT compensation
        #self.visa.write("COMSTC OFF")  # turn off LOAD compensation
        self.visa.write("BEEPWARN ON")  # sets the point averaging count (1 to 256, default 4)
        #self.visa.write("E4TP M1")

    # set settings function
    def wait_commands_exec(self):
        self.visa.write("*WAI")  # waits execution of all overlap commands sent before

    def set_measurement_parameters(self, meas='IMPH'): # measures Z and Theta (default)
        self.visa.write("MEAS {}".format(meas))

    def set_measurement_signals(self, mode='VOLT', level=0):
        self.visa.write("POWMOD {}".format(mode))  # set oscillator power mode
        self.visa.write("POWE {}".format(level))  # set oscillator power level (default volt 0.5, current 200e-6, volt: 5e-3 to 1 V, current: 200e-6 to 20e-3)

    def set_dc_bias(self, mode='VOLT', level=0, range=1e-3): # mode VOLT or
        self.visa.write("DCMOD {}".format(mode))  # select the DC output bias mode
        if mode == 'VOLT':
            self.visa.write("DCV {}".format(level))  # set the dc output bias level (+- 40 V)
        elif mode == 'CURR':
            self.visa.write("DCI {}".format(level))  # set the dc output bias level (+- 40 V)
        self.visa.write("DCRNG {}".format(self.a4294["dc_range"][range]))  # select the DC output bias mode

    # turn ON or OFF the dc bias
    def switch_dc_bias(self, state='OFF'):
        self.visa.write("DCO {}".format(state))  # turn off the dc bias (off by default)

    def set_averaging(self, bandwidth=5, point_averaging=4, average='OFF'):
        self.visa.write("BWFACT {}".format(bandwidth))  # sets the bandwidth (1 to 5,
        # 5: longest measurement time, accurate measurement)
        self.visa.write("PAVER {}".format(average))  # Enables/disables the point averaging function
        self.visa.write("PAVERFACT {}".format(point_averaging))  # sets the point averaging count (1 to 256, default 4)

    def set_oscillator_frequency(self, freq=1e6):
        self.visa.write("CWFREQ {}".format(freq)) # Sets the frequency of the oscillator for the oscillator (OSC) level sweep and dc bias level sweep

    def set_sweep_condition(self, parameter='FREQ', type='LOG', start=40, stop=10e6, points=201, point_delay=0, sweep_delay=0):
        self.visa.write("SWPP {}".format(parameter))        # sets the sweep parameter (default: frequency)
        self.visa.write("SWPT {}".format(type))             # set the sweep type to log (default: LIN)
        self.visa.write("STAR {}".format(start))       # sweep start freq (Hz)
        self.visa.write("STOP {}".format(stop))        # sweep stop freq (Hz)
        self.visa.write("POIN {}".format(points))      # number of points per sweep (deafult 201, max 801)
        self.visa.write("SDELT {}".format(sweep_delay))     # sets delay time for each sweep (deafult 0, max 30s)
        self.visa.write("PDELT {}".format(point_delay))     # sets delay time for each point (deafult 0, max 30s)

    def set_onscreen_arrangement(self): # sets autoscale on trace A and B (only for tool display)
        self.visa.write('TRAC A')
        self.visa.write('AUTO')
        self.visa.write('TRAC B')
        self.visa.write('AUTO')

    # read settings function
    def read_settings(self):
        settings = dict()
        settings["oscillator_power_mode"] = self.visa.query("POWMOD?")
        settings["oscillator_power_level"] = self.visa.query("POWE?")
        settings["dc_bias_mode"] = self.visa.query("DCMOD?")
        if self.visa.query("DCMOD?") == "VOLT":
            settings["dc_bias_level"].append(self.visa.query("DCV?"))
        elif self.visa.query("DCMOD?") == "CURR":
            settings["dc_bias_level"].append(self.visa.query("DCI?"))
        settings["bandwidth"] = self.visa.query("BWFACT?")
        settings["point_average"] = self.visa.query("PAVERFACT?")
        settings["sweep_delay"] = self.visa.query("SDELT?")
        settings["point_delay"] = self.visa.query("PDELT?")

        return settings

    # operation functions
    def fixture_compensation(self):
        #self.visa.write("HOLD")  # hold the trigger
    
        #self.visa.write("CALST OFF")  # turns off the user CALIBRATION off
        self.visa.write("E4TP OFF")  # adapter type NONE (E4TP M1: 1m extension, E4TP M2: 2m extension)
        self.visa.write("CALP USER")  # fixed frequency points (common for CALIB AND COMP)
    
        # compensation data definition
        #self.visa.write("DCOMOPENG 0")  # Sets the conductance value (G) of the OPEN standard you use
        #self.visa.write("DCOMOPENC 0")  # Sets the capacitance value (C) of the OPEN standard you use
        #self.visa.write("DCOMSHOR 0")  # Sets the resistance value (R) of the SHORT standard you use
        #self.visa.write("DCOMSHORL 0")  # Sets the inductance value (L) of the SHORT standard you use
        #self.visa.write("DCOMLOADR 1e4")  # Sets the resistance value (R) of the LOAD standard you use
        #self.visa.write("DCOMLOADL 0")  # Sets the inductance value (L) of the LOAD standard you use
        self.visa.write("*WAI")

    
        ans = input("Ready for open circuit compensation? [y/n]")
        self.visa.write("COMA")  # measures OPEN data
        self.visa.write("*WAI")  # waits execution of all overlap commands sent before
    
        print("Ready for short circuit compensation? [y/n]")
        answer = input()
        self.visa.write("COMB")  # measure SHORT data
        self.visa.write("*WAI")  # waits execution of all overlap commands sent before
    
        #print("Ready for load circuit compensation? [y/n]")
        answer = input()
        #self.visa.write("COMC")               # measure LOAD data
        #self.visa.write("*WAI")  # waits execution of all overlap commands sent before

        self.visa.write("COMSTA ON")  # turn on OPEN compensation
        self.visa.write("COMSTB ON")  # turn on SHORT compensation
        self.visa.write("COMSTC OFF")  # turn off LOAD compensation

        self.visa.write("ECALDON")  # turn off LOAD

    # sweep frequency on defined range and return modulus, phase and frequency
    def sweep_and_acquire(self):

        self.set_onscreen_arrangement()

        #self.wait_commands_exec()                # waits settings are ok
        self.visa.write("SING")                       # performs a single sweep. After the sweep mode goes to HOLD.
        #self.write("NUMG 10")                    # specify number of times
        #self.write("CONT")                       # continuous sweep
        #self.wait_commands_exec()                # waits
        self.visa.write("*WAI")

        # select trace A    (trace A and B are defined by MEAS)
        self.visa.write('TRAC A')
        nop = self.visa.query('POIN?')                        # ask for acquired points number
        a_data = self.visa.query_ascii_values('OUTPDTRC?')    # ask for acquired points number
        trace_a_readout = np.zeros(int(nop))
        trace_a_subsidiary = np.zeros(int(nop))
        for x in range(0, int(nop)):
            trace_a_readout[x] = a_data[2*x]        # readout
            trace_a_subsidiary[x] = a_data[2*x+1]   # subsidiary

        # select trace B (phase theta)
        self.visa.write('TRAC B')
        b_data = self.visa.query_ascii_values('OUTPDTRC?')
        trace_b_readout = np.zeros(int(nop))
        trace_b_subsidiary = np.zeros(int(nop))
        for x in range(0, int(nop)):
            trace_b_readout[x] = b_data[2*x]        # readout
            trace_b_subsidiary[x] = a_data[2*x+1]   # subsidiary

        freq = self.visa.query_ascii_values('OUTPSWPRM?')     # frequencies
        self.visa.write("*WAI")

        return freq, trace_a_readout, trace_b_readout
