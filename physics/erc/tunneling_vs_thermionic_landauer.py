import matplotlib.pyplot as plt
from scipy.constants import h, hbar, Boltzmann as kb, pi, e, m_e
from numpy import sqrt, exp, inf, heaviside, linspace, max, min, nanmax, zeros_like, zeros
from scipy.integrate import quad
from functions import *

"""Metal-Semiconductor-Metal --> E_C - E_F1 = E_B"""
V = 0.1  # voltage applied between the two contacts
E_C = 0.5  # conduction band bottom energy in eV
E_F1 = 0  # Fermi level of contact 1
E_F2 = E_F1 - V  # Fermi level of contact 2
E_B = E_C - E_F1  # barrier heigth in eV
T1 = 400  # temperature contact 1
T2 = 300  # temperature contact 2
L = 10e-9  # channel length
A = 1e-12  # channel section
epsilon_r = 2
E = linspace(E_F1 - 1, E_F1 + 1, 100000)


def I_E_3D(E, E_B, E_F1, E_F2, V, T1, T2, L, A):
    """
    :param E: [float] energy (eV)
    :param E_B: [float] barrier height (eV)
    :param E_F1: [float] Fermi level of contact 1 (eV)
    :param E_F2: [float] Fermi level of contact 2 (eV)
    :param T1: [float] temperature of contact 1 (Kelvin)
    :param T2: [float] temperature of contact 2 (Kelvin)
    :param L: [float] channel length (m)
    :param A: [float] channel section (m2)
    :return:
    """
    i_th = 2 * e / h * T_THERMIONIC_WITH_IMG_CHARGE(E, E_B, V, L, epsilon_r) * M_3D(E, E_C, A) * (f_FD(E, E_F1, T1) - f_FD(E, E_F2, T2))
    i_tu = 2 * e / h * T_TUNNELING(E, E_B, L) * M_3D(E, E_C, A) * (f_FD(E, E_F1, T1) - f_FD(E, E_F2, T2))
    return i_th, i_tu

plt.figure(1)
df = f_FD(E*e, E_F1*e, T1)-f_FD(E*e, E_F2*e, T2)
plt.plot(E, df/max(df), label="F1-F2")
plt.plot(E, M_3D(E*e, E_C*e, A=A) / max(M_3D(E*e, E_C*e, A=A)), label="M(E) 3D")
plt.plot(E, T_THERMIONIC(E*e, E_B*e, L) / max(T_THERMIONIC(E*e, E_B*e, L)), label="P(E) Thermionic")
plt.plot(E, T_TUNNELING(E*e, E_B*e, L) / max(T_TUNNELING(E*e, E_B*e, L)), label="P(E) Tunneling")
plt.legend()
#plt.fill_between(E, f_FD(E*e, E_F1*e, T1), 0, alpha=0.2)

plt.figure(2)
def i1E(E, E_B, E_C, E_F1, T1, E_F2, T2, L, A):
    return A * 2 * e / h * T_THERMIONIC(E*e, E_B*e, L) * M_3D(E*e, E_C*e, A) * (f_FD(E*e, E_F1*e, T1) - f_FD(E*e, E_F2*e, T2))
def i2E(E, E_B, E_C, E_F1, T1, E_F2, T2, L, A):
    return A * 2 * e / h * T_TUNNELING(E*e, E_B*e, L) * (f_FD(E*e, E_F1*e, T1) - f_FD(E*e, E_F2*e, T2))
Ls = linspace(1e-9, 20e-9, 101)
E_Bs = linspace(0.2, 2, 11)
I1 = zeros((len(E_Bs), len(Ls)))
I2 = zeros((len(E_Bs), len(Ls)))
for idx1, E_B in enumerate(E_Bs):
    for idx2, l in enumerate(Ls):
        I1[idx1, idx2] = quad(i1E, min(E), max(E), args=(E_B, E_C, E_F1, T1, E_F2, T1, l, A))[0]
        I2[idx1, idx2] = quad(i2E, min(E), max(E), args=(E_B, E_C, E_F1, T1, E_F2, T1, l, A))[0]
    L_t = hbar / (2 * kb * T1) * sqrt(e * E_B / m_e)
    print(E_B, L_t)
plt.figure(2)
for idx in range(I1.shape[0]):
    plt.plot(Ls*1e9, I1[idx, :] + I2[idx, :], label=E_Bs[idx])
plt.legend()
plt.show()




# print(f"{L_t / 1e-9} nm")