import numpy as np

# Parameters
n = 100  # Number of atoms
defect_index = n // 2
a = 1  # Lattice constant

t_0 = 0
t_max = 100
t_steps = 10000
t = np.linspace(t_0, t_max, t_steps, endpoint=False)
dt = t[1] - t[0]

x = np.linspace(0, n, n, endpoint=False) * a

k_h = 1.0  # Spring constant for host atoms
m_h = 1.0  # Mass of host atoms
k_g = 2.0  # Spring constant for guest atom
m_g = 2.0  # Mass of guest atom

# Initialize displacement arrays
u_t = np.zeros((n, t_steps))  # Displacements
u_prev = np.zeros(n)  # Displacement at t-dt
u_curr = np.zeros(n)  # Displacement at t
u_next = np.zeros(n)  # Displacement at t+dt

# Set initial conditions
u_curr[0] = 0.01  # Small displacement for the first atom

# Main time-stepping loop
for cur_t in range(1, t_steps - 1):
    for cur_n in range(n):
        # Apply boundary conditions for an infinite solid
        if cur_n == 0:
            left = 0  # Fixed at the left boundary
            right = u_curr[cur_n + 1]
        elif cur_n == n - 1:
            left = u_curr[cur_n - 1]
            right = 0  # Fixed at the right boundary
        else:
            left = u_curr[cur_n - 1]
            right = u_curr[cur_n + 1]

        # Equation of motion with defect
        if cur_n == defect_index:
            d2u_dt2 = (k_g / m_g) * (right + left - 2 * u_curr[cur_n])
        elif cur_n == defect_index - 1:
            d2u_dt2 = (k_g / m_h) * (right - u_curr[cur_n]) + (k_h / m_h) * (left - u_curr[cur_n])
        elif cur_n == defect_index + 1:
            d2u_dt2 = (k_h / m_h) * (right - u_curr[cur_n]) + (k_g / m_h) * (left - u_curr[cur_n])
        else:
            d2u_dt2 = (k_h / m_h) * (right + left - 2 * u_curr[cur_n])

        # Update displacement using Verlet integration
        u_next[cur_n] = 2 * u_curr[cur_n] - u_prev[cur_n] + d2u_dt2 * dt**2

    # Update arrays for the next time step
    u_prev[:] = u_curr
    u_curr[:] = u_next
    u_t[:, cur_t] = u_curr

# Plot the results
import matplotlib.pyplot as plt

# Animate or plot the displacement over time
plt.figure(figsize=(10, 6))
for i in range(0, t_steps, t_steps // 100):  # Plot a subset of time steps
    plt.plot(x, u_t[:, i], label=f"t = {i * dt:.2f}")
plt.xlabel("Atom Index")
plt.ylabel("Displacement")
plt.title("Wave Propagation in a Linear Chain with a Defect")
plt.legend(loc="upper right", fontsize=8)
plt.show()
