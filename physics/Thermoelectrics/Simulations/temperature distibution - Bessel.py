import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib
from scipy.special import kv
import scipy.integrate as integrate
from numpy import linspace, logspace, pi, sqrt, real, imag, log, sin, cos, ones_like, angle, zeros_like

'''Material properties Si'''
m_Si = 2330  # Kg/m3
k_Si = 230  # W/m/K
cv_Si = 700  # J/Kg/K

'''Material properties SiO2'''
m_SiO2 = 2650  # Kg/m3
k_SiO2 = 1.46  # W/m/K
cv_SiO2 = 680  # J/Kg/K

'''System properties'''
R = 100  # Ohm
I = 1e-3  # A
f0 = R * I**2 / (2 * 10e-6)  # W/m
w = 2 * pi * logspace(-1, 6, 1000)  # rad/s
T0 = 300  # K
r = 0.6e-6  # m
dr = 2.8e-6  # m
gamma = 0.5772156


"""Definitions"""
def K(k, m, cv):
    return k / m / cv

def q(w, K):
    return sqrt(1j * 2 * w / K)

def T(r, w, k, m, cv, f0, t=60):
    prefactor = 2 * f0 / (4 * pi * k)
    drift = -gamma + log(4 * K(k, m, cv) * t / r**2) + r**2 / (4 * K(k, m, cv) * t)
    im = 2 * imag((kv(0, r * q(w, K(k, m, cv)))))# * sin(2 * w * t)
    re = 2 * real((kv(0, r * q(w, K(k, m, cv)))))# * cos(2 * w * t)
    return  prefactor * (drift + im - re)

def T_DC(r, w, k, m, cv, f0, t):
    prefactor = 2 * f0 / (4 * pi * k)
    drift = -gamma + log(4 * K(k, m, cv) * t / r**2) + r**2 / (4 * K(k, m, cv) * t)
    return ones_like(w) * prefactor * drift

def T_X(r, w, k, m, cv, f0):
    prefactor = 2 * f0 / (4 * pi * k)
    im = 2 * imag((kv(0, r * q(w, K(k, m, cv)))))
    return prefactor * im

def T_Y(r, w, k, m, cv, f0):
    prefactor = 2 * f0 / (4 * pi * k)
    re = - 2 * real((kv(0, r * q(w, K(k, m, cv)))))
    return prefactor * re

"""Plot"""
grid = GridSpec(2, 3)
fig = plt.figure(figsize=(17 / 2.54, 12 / 2.54), dpi=300)
grid.update(top=0.94, bottom=0.18, left=0.08, right=0.98, hspace=0.5, wspace=0.5)
font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 8}

matplotlib.rc('font', **font)
ax00 = fig.add_subplot(grid[0, 0])
ax00.set_title("DC")
ax00.set_xlabel("f (Hz)")
ax00.set_ylabel(r"$\bar{\Delta T}_{DC}$ (K)")
ax01 = fig.add_subplot(grid[0, 1])
ax01.set_title("X-Y")
ax01.set_xlabel("f (Hz)")
ax01.set_ylabel("$\Delta T_{2_\omega, X}$ (K)")
ax02 = fig.add_subplot(grid[0, 2])
ax02.set_title("mod-phase")
ax02.set_xlabel("f (Hz)")
ax02.set_ylabel("$|\Delta T_{2\omega}|$ (K)")
ax10 = fig.add_subplot(grid[1, 0])
ax10.set_xlabel("f (Hz)")
ax10.set_ylabel(r"$\bar{T}_{DC}$ (K)")
ax11 = fig.add_subplot(grid[1, 1])
ax11.set_xlabel("f (Hz)")
ax11.set_ylabel(r"$\Delta T_{2_\omega, Y}$ (K)")
ax12 = fig.add_subplot(grid[1, 2])
ax12.set_xlabel("f (Hz)")
ax12.set_ylabel("\u2220$(\Delta T_{2_\omega})$ (°)")

"""Compute"""
TL_DC_SiO2 = T_DC(r, w, k_SiO2, m_SiO2, cv_SiO2, f0, 60)
TR_DC_SiO2 = T_DC(r + dr, w, k_SiO2, m_SiO2, cv_SiO2, f0, 60)
TL_X_SiO2 = T_X(r, w, k_SiO2, m_SiO2, cv_SiO2, f0)
TR_X_SiO2 = T_X(r + dr, w, k_SiO2, m_SiO2, cv_SiO2, f0)
TL_Y_SiO2 = T_Y(r, w, k_SiO2, m_SiO2, cv_SiO2, f0)
TR_Y_SiO2 = T_Y(r + dr, w, k_SiO2, m_SiO2, cv_SiO2, f0)

TL_DC_Si = T_DC(r, w, k_Si, m_Si, cv_Si, f0, 60)
TR_DC_Si = T_DC(r + dr, w, k_Si, m_Si, cv_Si, f0, 60)
TL_X_Si = T_X(r, w, k_Si, m_Si, cv_Si, f0)
TR_X_Si = T_X(r + dr, w, k_Si, m_Si, cv_Si, f0)
TL_Y_Si = T_Y(r, w, k_Si, m_Si, cv_Si, f0)
TR_Y_Si = T_Y(r + dr, w, k_Si, m_Si, cv_Si, f0)

T_avg_SiO2 = zeros_like(w)
T_avg_Si = zeros_like(w)
for idx, val in enumerate(w):
    T_avg_SiO2[idx] = integrate.quad(T, r, r + dr, (val, k_SiO2, m_SiO2, cv_SiO2, f0, 60))[0]/dr
    T_avg_Si[idx] = integrate.quad(T, r, r + dr, (val, k_Si, m_Si, cv_Si, f0, 60))[0]/dr

d_rho_SiO2 = abs((TL_X_SiO2 - TR_X_SiO2) + 1J * (TL_Y_SiO2 - TR_Y_SiO2))
d_phi_SiO2 = angle((TL_X_SiO2 - TR_X_SiO2) + 1J * (TL_Y_SiO2 - TR_Y_SiO2), deg=True)
d_rho_Si = abs((TL_X_Si - TR_X_Si) + 1J * (TL_Y_Si - TR_Y_Si))
d_phi_Si = angle((TL_X_Si - TR_X_Si) + 1J * (TL_Y_Si - TR_Y_Si), deg=True)
rho_SiO2 = abs(T_avg_SiO2 + 1J * T_avg_SiO2)
phi_SiO2 = angle(T_avg_SiO2 + 1J * T_avg_SiO2, deg=True)
rho_Si = abs(T_avg_Si + 1J * T_avg_Si)
phi_Si = angle(T_avg_Si + 1J * T_avg_Si, deg=True)

x = w / 2 / pi

ax00.semilogx(x, TL_DC_SiO2 - TR_DC_SiO2, label="$SiO_2$")
ax00.semilogx(x, TL_DC_Si - TR_DC_Si, label="$Si$")
ax00.fill_between(x, TL_DC_SiO2 - TR_DC_SiO2, TL_DC_Si - TR_DC_Si, alpha=0.3)
ax00.axvline(1, linestyle="--", linewidth=1, color="black")
ax00.axvline(1E3, linestyle="--", linewidth=1, color="black")
ax00.set_xticks([1e0, 1e2, 1e4, 1e6])

ax10.semilogx(x, T_avg_SiO2, label="$SiO_2$")
ax10.semilogx(x, T_avg_Si, label="$Si$")
ax10.fill_between(x, T_avg_SiO2, T_avg_Si, alpha=0.3)
ax10.axvline(1, linestyle="--", linewidth=1, color="black")
ax10.axvline(1E3, linestyle="--", linewidth=1, color="black")
ax10.set_xticks([1e0, 1e2, 1e4, 1e6])

ax01.semilogx(x, TL_X_SiO2 - TR_X_SiO2, label="$SiO_2$")
ax01.semilogx(x, TL_X_Si - TR_X_Si, label="$Si$")
ax01.fill_between(x, TL_X_SiO2 - TR_X_SiO2, TL_X_Si - TR_X_Si, alpha=0.3)
ax01.axvline(1, linestyle="--", linewidth=1, color="black")
ax01.axvline(1E3, linestyle="--", linewidth=1, color="black")
ax01.set_xticks([1e0, 1e2, 1e4, 1e6])

ax11.semilogx(x, TL_Y_SiO2 - TR_Y_SiO2, label="$SiO_2$")
ax11.semilogx(x, TL_Y_Si - TR_Y_Si, label="$Si$")
ax11.fill_between(x, TL_Y_SiO2 - TR_Y_SiO2, TL_Y_Si - TR_Y_Si, alpha=0.3)
ax11.axvline(1, linestyle="--", linewidth=1, color="black")
ax11.axvline(1E3, linestyle="--", linewidth=1, color="black")
ax11.set_xticks([1e0, 1e2, 1e4, 1e6])

ax02.loglog(x, d_rho_SiO2, label="$SiO_2$")
ax02.loglog(x, d_rho_Si, label="$Si$")
ax02.fill_between(x, d_rho_SiO2, d_rho_Si, alpha=0.3)
ax02.axvline(1, linestyle="--", linewidth=1, color="black")
ax02.axvline(1E3, linestyle="--", linewidth=1, color="black")
ax02.set_xticks([1e0, 1e2, 1e4, 1e6])

ax12.semilogx(x, d_phi_SiO2, label="$SiO_2$")
ax12.semilogx(x, d_phi_Si, label="$Si$")
ax12.fill_between(x, d_phi_SiO2, d_phi_Si, alpha=0.3)
ax12.axvline(1, linestyle="--", linewidth=1, color="black")
ax12.axvline(1E3, linestyle="--", linewidth=1, color="black")
ax12.set_xticks([1e0, 1e2, 1e4, 1e6])

plt.legend()
plt.show()
