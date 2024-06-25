import scipy.integrate as integrate
from numpy import exp, sqrt, inf, linspace, zeros, heaviside
from scipy.constants import Boltzmann as kB, elementary_charge as e, pi
import matplotlib.pyplot as plt

EF = 0
T = linspace(1, 500, 51)
mu = 1
sigma = 0.1


def fermi_dirac(E, EF, T):
    return 1 / (1 + exp((E - EF) / (kB * T / e)))


def gaussian(E, mu, sigma):
    return 1 / sqrt(2 * pi) / sigma * exp(-(E - mu) ** 2 / (2 * sigma ** 2))


def integrand(E, EF, T, mu, sigma):
    return E * fermi_dirac(E, EF, T) * (gaussian(E, mu, sigma) * heaviside(abs(mu - 3 * sigma), 1))


def norm(E, EF, T, mu, sigma):
    return fermi_dirac(E, EF, T) * (gaussian(E, mu, sigma) * heaviside(abs(mu - 3 * sigma), 1))


Eb = zeros(len(T))
for idx, val in enumerate(T):
    num = integrate.quad(integrand, 0, inf, (EF, val, mu, sigma))
    den = integrate.quad(norm, 0, inf, (EF, val, mu, sigma))
    Eb[idx] = num[0]/den[0]

plt.plot(T, Eb, 'o')
plt.xlabel("T (K)")
plt.ylabel("$\phi_0$ (eV)")
plt.show()