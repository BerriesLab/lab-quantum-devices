import matplotlib.pyplot as plt
from scipy.constants import h, hbar, Boltzmann as kb, pi, e, m_e, epsilon_0
from numpy import sqrt, exp, inf, linspace, ones
from scipy.integrate import quad

T = 300  # temperaure in Kelvin
E_b = 0.2  # barrier heigth in eV
v = 1

def thermionic(E_b, T, V, t, epsilon_r, A=120e4):
    a = A * T**2
    b = -E_b / (kb * T / e)
    c = sqrt(e * V / (4 * pi * epsilon_0 * epsilon_r * t))
    print(c)
    return a * exp(b) * exp(c)

def tunneling_fn(E_b, V, t):
    a = e**3 * (V / t)**2 / (16 * pi**2 *hbar * E_b * e)
    b = - 4 * t * sqrt(2 * m_e * (e * E_b)**3 ) / (3 * hbar * e * V)
    return a * exp(b)



#L_t = hbar / (2 * kb * T) * sqrt(e * phi / m_e)
#print(f"{L_t / 1e-9} nm")

t = linspace(1e-9, 100e-9, 100)
y_te = thermionic(0.5, 300, v, t, 3)
y_tu = tunneling_fn(0.5, v, t)
plt.plot(t, y_te)
plt.plot(t, y_tu)
plt.autoscale(True)
plt.yscale("log")
plt.show()
