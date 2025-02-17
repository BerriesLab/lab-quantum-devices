import matplotlib.pyplot as plt
from matplotlib import rc
import scipy as sci
import numpy as np
import mpmath as mp

# The material properties are given
kappa_SiO2 = 1.5 # W / m K
m_SiO2 = 2650 # kg / m3
cv_SiO2 = 1000 # J / kg K
K_SiO2 = kappa_SiO2 / ( m_SiO2 * cv_SiO2 ) # m2 / s

kappa_Si = 148 # W / m K
m_Si = 2329 # kg / m3
cv_Si = 700 # J / kg K
K_Si = kappa_Si / ( m_Si * cv_Si ) # m2 / s

rho_Au = 22.14 * 10**-9 # Ohm m
l = 100 * 10**-6 # m
A = 30 * 10**-9 * 3 * 10**-6 # m2
I0 = 0.001 # A
R = rho_Au*l/A

f0 = R*I0**2 / (2*m_SiO2*cv_SiO2*l*A)

print("Resistance = ", R, " Ohm")
print("Maximum total power dissipated = ", R*I0**2)
print("f0 = ", f0)

# Create input vector
# qr and eta
r1 = np.logspace(start=-9, stop=-3, num=1000)
dr = 5*10**-6
r2 = r1+dr
w_range = np.logspace(start=-2,stop=3,num=6)
for w in w_range:
    arg1 = (1j*w/K_Si)*r1
    arg2 = (1j*w/K_Si)*r2
    k0_1_Re = np.array([np.real(np.complex(mp.besselk(0,i))) for i in arg1])
    k0_1_Im = np.array([np.imag(np.complex(mp.besselk(0, i))) for i in arg1])
    k0_2_Re = np.array([np.real(np.complex(mp.besselk(0,i))) for i in arg2])
    k0_2_Im = np.array([np.imag(np.complex(mp.besselk(0, i))) for i in arg2])
    mean_k0_Re = (k0_1_Re+k0_2_Re)/2
    mean_k0_Im = (k0_1_Im - k0_2_Im)/2
#k0_2_Im = [np.imag(np.complex(mp.besselk(0,i))) for i in qr2]

#print("K Si = ", K_Si)
    plt.subplot(2,1,1)
    plt.semilogx(r1,delta_k0_Re)
    plt.subplot(2, 1, 2)
    plt.semilogx(r1, delta_k0_Im)
#plt.semilogx(qr2,k0_2_Re)
plt.legend([str(i)+" Hz" for i in w_range])
plt.xlabel("r1 (m)")
plt.ylabel(r'$DeltaK_0(qr)$')
plt.show()
