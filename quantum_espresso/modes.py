import numpy as np
import matplotlib.pyplot as plt

# Define constants
m = 1.0  # Mass of host atoms
M = 4.0  # Mass of defect atom
k_h = 1.0  # Spring constant for host atoms
k_g = 2.0  # Spring constant for guest atom
a = 1.0  # Lattice constant

# Define wavevector range (first Brillouin zone)
k_values = np.linspace(0, np.pi / a, 500)

# Eigenfrequencies
omega1 = np.sqrt((2 * k_h * (1 - np.cos(k_values))) / m)
omega2 = np.sqrt(((k_h + k_g) * (1 - np.cos(k_values))) / m)
omega3 = np.sqrt((2 * k_g * (1 - np.cos(k_values))) / M)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(k_values, omega1, label=r'$\omega_1 = \sqrt{\frac{2k_h(1-\cos k)}{m}}$', lw=2)
plt.plot(k_values, omega2, label=r'$\omega_2 = \sqrt{\frac{(k_h + k_g)(1-\cos k)}{m}}$', lw=2)
plt.plot(k_values, omega3, label=r'$\omega_3 = \sqrt{\frac{2k_g(1-\cos k)}{M}}$', lw=2)

# Adding labels, title, and legend
plt.xlabel(r'Wavevector $k$', fontsize=14)
plt.ylabel(r'Angular Frequency $\omega$', fontsize=14)
plt.title('Dispersion Relation: Eigenfrequencies vs. Wavevector', fontsize=16)
plt.legend(fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)

# Show the plot
plt.tight_layout()
plt.show()

