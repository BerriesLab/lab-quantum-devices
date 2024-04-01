import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib
import numpy as np
from scipy.special import kv
from scipy.optimize import curve_fit

file = r"C:\Users\dabe\Google Drive\Work\Projects\2019 - QuIET\Experimental\Data\tep_frequency_dependence.txt"
data = np.loadtxt(file, skiprows=2)

f = data[:, 0]
a = data[:, 1]
p = data[:, 2]

mask = np.where(f < 10)
p[mask] = abs(p[mask])
mask = np.where(f > 230)
p[mask] = p[mask] - 180
mask = np.where(f > 1800)
p[mask] = p[mask] - 180

a = a / a.max()

x = a * np.cos(np.deg2rad(p))
y = a * np.sin(np.deg2rad(p))

fig = plt.figure(figsize=(30 / 2.54, 15 / 2.54))
grid = matplotlib.gridspec.GridSpec(nrows=2, ncols=2)
# ------------------------------------
ax1 = fig.add_subplot(grid[0, 0])
ax1.set_xlabel("f (Hz)")
ax1.set_ylabel("Amplitude (I)")
ax1.loglog(f, a, 'o', label="amplitude")
# ------------------------------------
ax2 = fig.add_subplot(grid[1, 0])
ax2.set_xlabel("f (Hz)")
ax2.set_ylabel("Phase (°)")
ax2.semilogx(f, p, 'o', label="phase")
# ------------------------------------
ax3 = fig.add_subplot(grid[:, 1])
ax3.set_xlabel("f (Hz)")
ax3.set_ylabel("x-component")
ax3.semilogx(f, x, 'o', color="red", label="x")
ax3.semilogx(f, y, 'o', color="green", label="y")
# ------------------------------------

''' Fitting '''
# kn(n, x) is the modified Bessel function (of x) of the second kind of order n


def sinfunc(x, a, b, c, r, dr):
    # x: frequency
    # a: effective thermal diffusivity
    # b: power dissipated per unit length
    # c: effective thermal conductivity = K * m * cv
    return b / (4 * np.pi * c) * (np.imag(kv(0, np.sqrt(1j * 2 * (2 * np.pi * x) / a) * r) -
                                          kv(0, np.sqrt(1j * 2 * (2 * np.pi * x) / a) * (r + dr))))


def cosfunc(x, a, b, c, r, dr):
    # x: frequency
    # a: effective thermal diffusivity
    # b: power dissipated per unit length
    # c: effective thermal conductivity = K * m * cv
    return - b / (4 * np.pi * c) * (np.real(kv(0, np.sqrt(1j * 2 * (2 * np.pi * x) / a) * r) -
                                            kv(0, np.sqrt(1j * 2 * (2 * np.pi * x) / a) * (r + dr))))


# to fit complex data one must create ff and yy, i.e. concatenated arrays of real and imaginary values
# p0 is the initial guess
# The model function, f(x, …) must take the independent variable as the first argument
# and the parameters to fit as separate remaining arguments.
r = 1e-6
dr = 1e-6
f0 = 100 * 1e-3 * 1e-3 / 2e-6
popt, pcov = curve_fit(sinfunc, f, x) # x and y are my data points
ax3.semilogx(f, sinfunc(f, popt[0], popt[1], popt[2], popt[3], popt[4]), label="x")
# ax3.semilogx(f, sinfunc(f, 8.3e-7, f0, 5, r, dr), label="x")
# ax3.semilogx(f, cosfunc(f, 8.3e-7, f0, 5, r, dr), label="y")
# w = 2 * np.pi * f
# q = np.sqrt(1j * 2 * w / K)
# T = 2 * f0 / (4 * np.pi * k) * np.imag(K0(q * r)) * np.sin(2 * w * t)
# T = - 2 * f0 / (4 * np.pi * k) * np.real(K0(q * r)) * np.cos(2 * w * t)

# f0 is the time-independent-component energy dissipated per unit length and time
# f0 = R0 * I0 ** 2
# dTx = f0 / (4 * np.pi * k) * np.imag(K0(q * r))
# dTy = - f0 / (4 * np.pi * k) * np.real(K0(q * r))

plt.legend()
plt.show()