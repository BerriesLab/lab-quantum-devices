from numpy import linspace, exp, sqrt, zeros_like
from scipy.constants import Boltzmann as kB, elementary_charge as e
import matplotlib.pyplot as plt

"""Refer energy to the conduction band bottom"""
E = linspace(-300e-3, 300e-3, 1000)
Eg = 0.1
T1 = 300
T2 = 250
mu1 = 0
mu2 = 0
U1 = 0
U2 = 0


def FD(E, mu, U, T):
    return 1 / (1 + exp((E - (mu - U)) / (kB * T / e)))


def D3D(E, Eg):
    D = zeros_like(E)
    D[E <= -Eg] = sqrt(-(E[E <= -Eg] + Eg))
    D[E >= 0] = sqrt(E[E >= 0])
    return D


def DGr(E):
    D = zeros_like(E)
    D[E <= 0] = E[E <= 0]
    D[E >= 0] = E[E >= 0]
    return D


f1 = FD(E, mu1, U1, T1)
# plt.plot(f1/max(f1), E)
f2 = FD(E, mu2, U2, T2)
# plt.plot(f2/max(f2), E)
df = FD(E, mu1, U1, T1) - FD(E, mu2, U2, T2)
plt.plot(df/max(df), E)
dos = D3D(E, Eg)
plt.plot(dos/max(dos), E)
plt.fill_betweenx(E, dos/max(dos), 0, alpha=0.3)
p = dos * df
plt.plot(p/max(p), E)
plt.show()

