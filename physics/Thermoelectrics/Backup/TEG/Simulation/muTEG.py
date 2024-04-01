from scipy.optimize import fsolve
from scipy.fft import fft
from numpy import sin, pi, linspace, zeros
import matplotlib.pyplot as plt

"""Define muTEG architecture"""
l = 100e-6  # thermocouple lenght (in m)
H1 = 1e5    # thermal conductance of interface 1 (in W / m2 / K2)
Ks1 = 1     # thermal conductance of substrate 1 (in W / m2 / K2)
Kpn = 10    # thermal conducatnce of the thermocouple (in W / m2 / K2)
apn = 1000e-6  # relative Seebeck coefficient of the thermocouple (in V/K)
Rpn = 1e3   # electrical resistance series of the thermocouple (in Ohm)
Ks2 = Ks1   # thermal conductance of substrate 2 (in W / m2 / K2)
H2 = H1     # thermal conductance of interface 2 (in W / m2 / K2)

"""Define simulation parameters"""
t = linspace(0, 60, 10000)

f = 0.10  # Hz
w = 2 * pi * f
Tr1dc = 1
Tr2dc = 0
Tr1w = 1




def func(x, Tr1, Tr2, H1, Ks1, Kpn, apn, Rpn, Ks2, H2):
    """
    :param x: temperture vector
                x[0]: Ts1
                x[1]: T1
                x[2]: T2
                x[3]: Ts2
    :param H1:
    :param Ks1:
    :param Kpn:
    :param apn:
    :param Rpn:
    :param Ks2:
    :param H2:
    :return:

    """
    out = [H1 * (Tr1 - x[0]) - Ks1 * (x[0] - x[1]),
           Ks1 * (x[0] - x[1]) - Kpn * (x[1] - x[2]) - (apn * (x[1] - x[2])) ** 2 / (2 * Rpn) - apn ** 2 * (x[1] - x[2]) * x[1] / Rpn,
           Ks1 * (x[2] - x[3]) - Kpn * (x[1] - x[2]) - (apn * (x[1] - x[2])) ** 2 / (2 * Rpn) + apn ** 2 * (x[1] - x[2]) * x[2] / Rpn,
           Ks2 * (x[2] - x[3]) - H2 * (x[3] - Tr2)]

    return out


result = zeros((len(t), 4))
for idx, val in enumerate(t):
    Tr1 = Tr1dc + Tr1w * sin(2 * w * val)
    Tr2 = Tr2dc
    root = fsolve(func, [300, 300, 300, 300], (Tr1, Tr2, H1, Ks1, Kpn, apn, Rpn, Ks2, H2))
    result[idx, :] = root

four = fft(result[:, 1])


#plt.plot(t, result[:, 1])
#plt.plot(t, result[:, 2])
plt.plot(four, t)
plt.show()
