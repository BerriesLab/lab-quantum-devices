import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

T = 2000               # Total number of time steps

# Parameters for the atomic chain
N = 100               # Number of atoms
m0 = 1.0              # Mass of host atoms
mg = 2.0              # Mass of guest atom
k = 1.0               # Spring constant
ng = 70               # Position of the guest atom (index in the chain)
a = 10                # Inter-atomic distance (in A)

# Build lattice
x = np.arange(N) * a


masses = np.ones(N) * m0  # All host atoms have mass m0
masses[ng] = mg           # Set the guest atom's mass to mg
A = 0.1               # Amplitude of the wave packet
sigma = 5.0 * a       # Width of the Gaussian wave packet (in A)
k0 = 2.0              # Wave number of the wave packet
x0 = 20 * a           # Initial position of the wave packet (center)
f = 1                 # Frequency of the oscillation (in Hz)
omega = 2 * np.pi * f

# Initial displacement (u) - Initial velocity (v) - at time t = 0
t = 0
u = A * np.exp(-((x - x0)**2) / (2 * sigma**2)) * np.cos(k0 * x - omega * t)
v = - omega * A * np.exp(-((x - x0)**2) / (2 * sigma**2)) * np.sin(k0 * x - omega * t)

# Use the velocity to calculate the first step in Verlet integration
dt = 0.1              # Time step
u_prev = u - dt * v   # Backward integration for the initial step

# Store displacements for visualization
frames = []


# Time evolution loop
for t in range(T):
    u_next = np.zeros_like(u)
    u_next[1:-1] = (2 * u[1:-1] - u_prev[1:-1] + dt ** 2 / masses[1:-1] * k * (u[2:] - 2 * u[1:-1] + u[:-2]))
    u_prev, u = u, u_next  # Update displacements for the next iteration
    frames.append(u.copy())

# Set up the figure
fig, ax = plt.subplots()
line, = ax.plot(frames[0])  # Plot the first frame
ax.set_ylim(-1, 1)          # Set y-axis limits
ax.set_xlabel('Atom index')
ax.set_ylabel('Displacement')
ax.axvline(ng, color='red', linestyle='--', label='Guest Atom')
ax.legend()

# Animation function
def animate(i):
    line.set_ydata(frames[i])  # Update the y-data for the line
    return line,

# Create the animation
ani = FuncAnimation(fig, animate, frames=len(frames), interval=50)
plt.show()