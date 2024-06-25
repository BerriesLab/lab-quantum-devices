import scipy.integrate as integrate
from numpy import array, where, zeros, sqrt, linspace, sinh, exp, concatenate, flip, ceil, nan, zeros_like, empty, unique, log10, sin, sinc, log
from scipy.constants import Boltzmann as k_b, elementary_charge as e, pi, electron_mass as m_e, h, epsilon_0, hbar
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import matplotlib.cm
from lmfit import Model

class FitFN:

    def __init__(self, V, I, epsilon_r, phi, d, T):
        self.V = V
        self.I = I
        self.epsilon_r = epsilon_r
        self.phi = phi
        self.d = d
        self.T = T





    def E(self, x):
        func = lambda t: sqrt(1 - x**2 * sin(t)**2)
        return integrate.quad(func, 0, pi/2)[0]

    def K(self, x):
        func = lambda t: 1 / sqrt(1 - x**2 * sin(t)**2)
        return integrate.quad(func, 0, pi/2)[0]

    def v(self, y):
        a = sqrt(1 - y**2)
        z = sqrt(2 * a / (1 + a))
        return sqrt((1 + a) / 2) * self.E(z) - (1 - a) * sqrt((1 + a)/2) * self.K(z)

    def t(self, y):
        a = sqrt(1 - y**2)
        z = sqrt(2 * a / (1 + a))
        return sqrt((1 + a) / 2) * self.E(z)

    def c(self, y):
        F = self.V / self.d
        return 2 * sqrt(2) / F * sqrt(self.phi) * self.t(y)

    def func(self, V, phi, d, T):
        F = V / d
        z = sqrt(F) / phi
        A = F ** 2 / (16 * pi * phi * self.t(z)**2)
        B = pi * self.c(z) * k_b * T / (sin(pi * self.c(z) * k_b * T))
        C = exp(-4 * sqrt(2) * phi**(3/2) * self.v(z) / (3 * F))
        return A * B * C

    def iv_fit(self, weights=1):
        x = 1 / v
        y = log(i / v**2)
        model = Model(func=self.func, nan_policy="propagate")  # create model object
        # print(f"Parameters: {model.param_names}")
        # print(f"Independent variable: {model.independent_vars}")
        model.set_param_hint('phi01', value=self.phi01_ini, vary=self.phi01_vary, min=self.phi01_min, max=self.phi01_max)  # set parameter phi01 to passed argument
        model.set_param_hint('phi02', value=self.phi02_ini, vary=self.phi02_vary, min=self.phi02_min, max=self.phi02_max)  # set parameter phi02 to passed argument
        model.set_param_hint('T', value=self.T_ini, vary=self.T_vary, min=self.T_min, max=self.T_max)  # set parameter T to passed argument
        model.set_param_hint('S1', value=self.S1_ini, vary=self.S1_vary, min=self.S1_min, max=self.S1_max)  # set parameter S1 to passed argument
        model.set_param_hint('S2', value=self.S2_ini, vary=self.S2_vary, min=self.S2_min, max=self.S2_max)  # set parameter S2 to passed argument
        model.set_param_hint('n1', value=self.n1_ini, vary=self.n1_vary, min=self.n1_min, max=self.n1_max)
        model.set_param_hint('n2', value=self.n2_ini, vary=self.n2_vary, min=self.n2_min, max=self.n2_max)
        model.set_param_hint('v1', value=self.v1_ini, vary=self.v1_vary, min=self.v1_min, max=self.v1_max)
        model.set_param_hint('v2', value=self.v2_ini, vary=self.v2_vary, min=self.v2_min, max=self.v2_max)
        params = model.make_params()  # generate parameter objects
        result = model.fit(self.I, params, V=self.V, weights=weights)
        return result