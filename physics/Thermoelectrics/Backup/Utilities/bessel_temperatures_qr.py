import matplotlib.pyplot as plt
from numpy import array, linspace, logspace, sin, cos, pi, log, imag, real, sqrt, ones, zeros
from scipy.special import kv
from scipy.integrate import quad
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
import matplotlib.cm as cm

# SiO2
mSiO2 = 2650  # kg / m3
cvSiO2 = 680  # J / k / Kg
kSiO2 = 1.46  # W / m / K

# Si
mSi = 2330
cvSi = 700
kSi = 130

f = logspace(-1, 6, 1001)
r = 0.6e-6  # m
dr = 2.8e-6  # m
I = 1e-3
R = 100
l = 8e-6
P = R * I**2
p = P / l


def T(r, f, t, f0, k, m, cv, what="full"):

    """Return temperature drift and oscillations amplitude"""

    w = 2 * pi * f
    K = k / m / cv
    q = sqrt(1j * 2 * w / K)
    A = f0 / 4 / pi / k * 2
    B = 0.5772156
    C = log(4 * K * t / r**2) + r**2 / 4 / K / t
    D = 2 * imag(kv(0, q * r))# * ones(len(t))
    E = 2 * real(kv(0, q * r))# * ones(len(t))

    if what == "full":
        output = A * (-B + C), A * D / 2, - A * E / 2

    if what == "dc":
        output = A * (-B + C)

    if what == "x":
        output = A * D / 2

    if what == "y":
        output = - A * E / 2

    return output


t1_Si = T(f=f, t=10, f0=p, k=kSi, r=r, m=mSi, cv=cvSi)
t2_Si = T(f=f, t=10, f0=p, k=kSi, r=r+dr, m=mSi, cv=cvSi)
t1_SiO2 = T(f=f, t=10, f0=p, k=kSiO2, r=r, m=mSiO2, cv=cvSiO2)
t2_SiO2 = T(f=f, t=10, f0=p, k=kSiO2, r=r+dr, m=mSiO2, cv=cvSiO2)

tavg_Si_dc = zeros(len(f))
tavg_Si_x = zeros(len(f))
tavg_Si_y = zeros(len(f))
tavg_SiO2_dc = zeros(len(f))
tavg_SiO2_x = zeros(len(f))
tavg_SiO2_y = zeros(len(f))
for idx, val in enumerate(f):
    tavg_Si_dc[idx] = quad(T, r, r+dr, args=(val, 3*60, p, kSi, mSi, cvSi, "dc"))[0]/dr
    tavg_Si_x[idx] = quad(T, r, r+dr, args=(val, 3*60, p, kSi, mSi, cvSi, "x"))[0]/dr
    tavg_Si_y[idx] = quad(T, r, r+dr, args=(val, 3*60, p, kSi, mSi, cvSi, "y"))[0]/dr
    tavg_SiO2_dc[idx] = quad(T, r, r+dr, args=(val, 3*60, p, kSiO2, mSiO2, cvSiO2, "dc"))[0]/dr
    tavg_SiO2_x[idx] = quad(T, r, r+dr, args=(val, 3*60, p, kSiO2, mSiO2, cvSiO2, "x"))[0]/dr
    tavg_SiO2_y[idx] = quad(T, r, r+dr, args=(val, 3*60, p, kSiO2, mSiO2, cvSiO2, "y"))[0]/dr

grid = GridSpec(2, 3)
fig = plt.figure(figsize=(30 / 2.54, 15 / 2.54))
grid.update(top=0.93,
            bottom=0.11,
            left=0.07,
            right=0.95,
            hspace=0.31,
            wspace=0.33)

ax0 = fig.add_subplot(grid[0, 0])
ax1 = fig.add_subplot(grid[0, 1])
ax2 = fig.add_subplot(grid[0, 2])
ax3 = fig.add_subplot(grid[1, 0])
ax4 = fig.add_subplot(grid[1, 1])
ax5 = fig.add_subplot(grid[1, 2])
ax0.set_xlabel("f (Hz)")
ax0.set_ylabel("$\Delta T_{DC}$ (K)")
ax1.set_xlabel("f (Hz)")
ax1.set_ylabel("$\Delta T_{2\omega ,X}$ (K)")
ax2.set_xlabel("f (Hz)")
ax2.set_ylabel("$\Delta T_{2\omega, Y}$ (K)")
ax3.set_xlabel("f (Hz)")
ax3.set_ylabel("$\overline{T}_{DC}$ (K)")
ax4.set_xlabel("f (Hz)")
ax4.set_ylabel("$\overline{T}_{2\omega ,X}$ (K)")
ax5.set_xlabel("f (Hz)")
ax5.set_ylabel("$\overline{T}_{2\omega, Y}$ (K)")

ax0.fill_between(f, (t1_Si[0]-t2_Si[0])*ones(len(f)), (t1_SiO2[0]-t2_SiO2[0])*ones(len(f)), alpha=0.4)
ax0.semilogx(f, (t1_Si[0]-t2_Si[0])*ones(len(f)), linestyle="--", label="Si")
ax0.semilogx(f, (t1_SiO2[0]-t2_SiO2[0])*ones(len(f)), linestyle="-.", label="SiO2")
ax0.axvline(1, ymin=0, ymax=1, linestyle="-.", color="grey")
ax0.axvline(20, ymin=0, ymax=1, linestyle="-.", color="grey")

ax1.fill_between(f, t1_Si[1]-t2_Si[1], t1_SiO2[1]-t2_SiO2[1], alpha=0.4)
ax1.semilogx(f, t1_Si[1]-t2_Si[1], linestyle="--", label="Si")
ax1.semilogx(f, t1_SiO2[1]-t2_SiO2[1], linestyle="-.", label="SiO2")
ax1.axvline(1, ymin=0, ymax=1, linestyle="-.", color="grey")
ax1.axvline(20, ymin=0, ymax=1, linestyle="-.", color="grey")

ax2.fill_between(f, (t1_Si[2]-t2_Si[2]), (t1_SiO2[2]-t2_SiO2[2]), alpha=0.4)
ax2.semilogx(f, (t1_Si[2]-t2_Si[2]), linestyle="--", label="Si")
ax2.semilogx(f, (t1_SiO2[2]-t2_SiO2[2]), linestyle="-.", label="SiO2")
ax2.axvline(1, ymin=0, ymax=1, linestyle="-.", color="grey")
ax2.axvline(20, ymin=0, ymax=1, linestyle="-.", color="grey")

ax3.fill_between(f, tavg_Si_dc, tavg_SiO2_dc, alpha=0.4)
ax3.semilogx(f, tavg_Si_dc, linestyle="--", label="Si")
ax3.semilogx(f, tavg_SiO2_dc, linestyle="-.", label="SiO2")
ax3.axvline(1, ymin=0, ymax=1, linestyle="-.", color="grey")
ax3.axvline(20, ymin=0, ymax=1, linestyle="-.", color="grey")

ax4.fill_between(f, tavg_Si_x, tavg_SiO2_x, alpha=0.4)
ax4.semilogx(f, tavg_Si_x, linestyle="--", label="Si")
ax4.semilogx(f, tavg_SiO2_x, linestyle="-.", label="SiO2")
ax4.axvline(1, ymin=0, ymax=1, linestyle="-.", color="grey")
ax4.axvline(20, ymin=0, ymax=1, linestyle="-.", color="grey")

ax5.fill_between(f, tavg_Si_y, tavg_SiO2_y, alpha=0.4)
ax5.semilogx(f, tavg_Si_y, linestyle="--", label="Si")
ax5.semilogx(f, tavg_SiO2_y, linestyle="-.", label="SiO2")
ax5.axvline(1, ymin=0, ymax=1, linestyle="-.", color="grey")
ax5.axvline(20, ymin=0, ymax=1, linestyle="-.", color="grey")

plt.legend()
plt.show()