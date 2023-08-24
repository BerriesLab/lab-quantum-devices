from scipy.constants import h, hbar, Boltzmann as kb, pi, e, m_e, epsilon_0
from numpy import sqrt, exp, inf, heaviside

def f_FD(E, E_F, T):
    """Fermi-Dirac distribution"""
    return 1 / (1 + exp((E - E_F) / (kb * T)))

def D_1D(E, E_C):
    """
    :param E: [float] energy
    :param E_C: [float] conduction band bottom energy
    :return: [function of energy E] the density of states per unit energy per unit length of a 1D electron gas.
    """
    return 1 / (pi * hbar) * sqrt(2 * m_e / abs(E- E_C)) * heaviside(E - E_C, 1)

def D_2D(E, E_C):
    """
    :param E: [float] energy
    :param E_C: [float] conduction band bottom energy
    :return: [function of energy E] the density of states per unit energy per unit length of a 2D electron gas.
    """
    return m_e / (pi * hbar**2) * heaviside(E - E_C, 1)

def D_3D(E, E_C):
    """
    :param E: [float] energy
    :param E_C: [float] conduction band bottom energy
    :return: [function of energy E] the density of states per unit energy per unit length of a 3D electron gas.
    """
    return m_e * sqrt(2 * m_e * abs(E - E_C)) / (pi**2 * hbar**3) * heaviside(E - E_C, 1)

def v_x_1D(E, E_C):
    """Assuming the conduction band bottom as the energy reference.
    :param E: [float] energy
    :param E_C: [float] conduction band bottom energy
    :return: <v_x+> = v = sqrt(2 * (E - E_C) / m) the average velocity in 1D the x+ direction from contact 1 to contact 2
    """
    return sqrt(2 * (E - E_C) / m_e) * heaviside(E - E_C, 1)

def v_x_2D(E, E_C):
    """Assuming the conduction band bottom as the energy reference.
    :param E: [float] energy
    :param E_C: [float] conduction band bottom energy
    :return: <v_x+> = v/2 = sqrt((E-E_C) / (2*m)) the average velocity in 2D in the x+ direction from contact 1 to contact 2
    """
    return 2 / pi * sqrt(2 * (E - E_C) / m_e) * heaviside(E - E_C, 1)

def v_x_3D(E, E_C):
    """Assuming the conduction band bottom as the energy reference.
    :param E: [float] energy
    :param E_C: [float] conduction band bottom energy
    :return: <v_x+> = v/2 = sqrt((E-E_C) / (2*m)) the average velocity in 3D in the x+ direction from contact 1 to contact 2
    """
    return 1 / 2 * sqrt(2 * abs(E - E_C) / m_e) * heaviside(E - E_C, 1)

def M_1D(E, E_C):
    """
    :param E: [float] energy
    :return: [function of energy E] the number of modes per unit energy in 1D
    """
    return h / 4 * v_x_1D(E, E_C) * D_1D(E, E_C)

def M_2D(E, E_C, W):
    """
    :param E: [float] energy
    :param W: [float] width of the channel
    :return: [function of energy E] the number of modes per unit energy in 2D
    """
    return W * h / 4 * v_x_2D(E, E_C) * D_2D(E, E_C)

def M_3D(E, E_C, A):
    """
    :param E: [float] energy
    :param A: [float] section of the channel
    :return: [function of energy E] the number of modes per unit energy in 3D
    """
    return A * h / 4 * v_x_3D(E, E_C) * D_3D(E, E_C) * heaviside(E-E_C, 1)

def T_L(E, Lambda, L):
    """
    Transmission probability
    :param E: [float] energy
    :param Lambda: [function of energy E] electron mean free path for backscattering
    :param L: [float] channel length
    :return: [function of energy E] the transmission probability
    """
    return Lambda(E) / (Lambda(E) + L)

def T_THERMIONIC(E, E_B, L):
    """Ideal thermionic emission occurs when the electron energy is higher than E_B
    :param E: [float] energy in eV
    :param E_B: [float] barrier heigth in eV
    :param L: [float] barrier thickness in m
    :return: [float] transmission probability at energy E
    """
    return heaviside(E - E_B, 1)

def T_THERMIONIC_WITH_IMG_CHARGE(E, E_B, V, L, epsilon_r):
    """Correct the barrier height to account for the image charge lowering effect
    :param E: [float] energy in eV
    :param E_B: [float] barrier height in eV
    :param L: [float] barrier thickness in m
    :return: [float] the transmission probability at energy E
    """
    E_B_img = E_B - sqrt(e * V / (4 * pi * epsilon_0 * epsilon_r * L))
    return heaviside(E - E_B_img, 1)

def T_TUNNELING(E, E_B, L):
    """
    :param E: [float] energy in eV
    :param E_B: [float] barrier height in eV
    :param L: [float] barrier thickness
    :return: [float] the transmission probability at energy E
    """
    return exp(-2 * sqrt(2 * m_e / hbar**2 * abs(E_B - E)) * L) * heaviside(E_B - E, 1)