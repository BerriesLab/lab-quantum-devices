import matplotlib.pyplot as plt
from scipy.constants import h, hbar, Boltzmann as kb, pi, e, m_e
from numpy import sqrt, exp, inf
from scipy.integrate import quad


T = 300  # temperaure in Kelvin
E_b = 0.2  # barrier heigth in eV

def fd(E, E_F, T):
    """Fermi-Dirac distribution"""
    return 1 / (1 + exp((E - E_F) / (kb * T)))

def g(E):
    """Density of states (per unit energy per unit volume) of a 3D electron gas"""
    return 1 / (2 * pi**2) * (2 * m_e / hbar**2)**(3/2) * sqrt(E)

def v_x(E):
    """Assuming that the energy of the electrons above the Fermi level is entirely kinetic."""
    v_x = sqrt(E / (2 * m_e))
    return v_x


def j(v_x, g):
    """
    :param v_x: [function of energy E] is the velocity expressed as a function of energy
    :param g: [function of energy E] is the density of states per unit volume per unit energy
    :return: [A/m2] the density of current
    """
    j = e * quad(lambda E: v_x(E) * g(E) * fd(E), 0, inf)

def probability_tunneling(E, E_b, d):
    alpha = sqrt(2 * m_e * (E_b - E) / hbar**2)
    p_E = exp(-2 * alpha * d)
    return p_E

def probability_thermionic(E, E_b, T):
    p_E = exp(-(E_b - E) / (kb * T))
    return p_E

def current_electric_tunneling(E):
    j_E = e * v_R(E) * n(E) * probability_tunneling(E, E_b)
    j = quad(j_E, 0, inf)
    return j

def current_electric_thermionic(E):
    j_E = e * v_R(E) * n(E) * probability_thermionic(E, E_b, T)
    j = quad(j_E, 0, inf)
    return j

def current_thermal_tunneling(E):




L_t = hbar / (2 * kb * T) * sqrt(e * phi / m_e)
print(f"{L_t / 1e-9} nm")