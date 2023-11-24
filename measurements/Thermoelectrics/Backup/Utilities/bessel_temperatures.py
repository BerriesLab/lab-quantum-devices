import matplotlib.pyplot as plt
from numpy import array, linspace, logspace, sin, cos, pi, log, imag, real, sqrt, ones
from scipy.special import kv

# SiO2
m = 2650  # kg / m3
cv = 680  # J / k / Kg
k = 1.46  # W / m / K
f = logspace(-3, 6, 41)
t = linspace(1, 5*60, 1000)
r = 0.6e-6  # m
dr = 2.8e-6  # m
I = 1e-3
R = 100
l = 8e-6
P = R * I**2
p = P / l


def T(f, t, f0, k, r, m, cv):

    """Return temperature drift and oscillations amplitude"""

    w = 2 * pi * f
    K = k / m / cv
    q = sqrt(1j * 2 * w / K)
    A = f0 / 4 / pi / k * 2
    B = 0.5772156
    C = log(4 * K * t / r**2) + r**2 / 4 / K / t
    D = 2 * imag(kv(0, q * r))# * ones(len(t))
    E = 2 * real(kv(0, q * r))# * ones(len(t))

    return A * (-B + C), A * D / 2, - A * E / 2


def dT(f, f0, k, r, dr, m, cv):

    w = 2 * pi * f
    K = k / m / cv
    q = sqrt(1j * 2 * w / K)
    A = f0 / 4 / pi / k * 2
    B = log(1 + dr / r)
    C = 2 * imag(kv(0, q * r) - kv(0, q * (r + dr)))
    D = 2 * real(kv(0, q * r) - kv(0, q * (r + dr)))

    return A * B, A * C / 2, - A * D / 2


print(f"Power [W/m]: {p}")
print(f"Thermal diffusivity [m2/s]: {k/m/cv}")

t1 = T(f=f, t=10, f0=p, k=k, r=r, m=m, cv=cv)
t2 = T(f=f, t=10, f0=p, k=k, r=r+dr, m=m, cv=cv)

#plt.plot(f, t1[0]-t2[0], linestyle="dotted")
w = 2 * pi * f
K = k / m / cv
q = sqrt(1j * 2 * w / K)
plt.semilogx(q*r, t1[1]-t2[1], linestyle="--")
plt.semilogx(q*r, -(t1[2]-t2[2]), linestyle="-.")

plt.show()