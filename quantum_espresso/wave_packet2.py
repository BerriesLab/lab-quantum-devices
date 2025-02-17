import numpy as np
import matplotlib.pyplot as plt


n = 100  # Number of atoms
defect_index = n // 2  # Place a defect in the center
a = 1  # Lattice constant
x = np.linspace(0, n, n, endpoint=False) * a  # Lattice

t_0 = 0  # Initial time (s)
t_max = 100  # Final time (s)
t_steps = 100000  # Number of steps
t = np.linspace(t_0, t_max, t_steps, endpoint=False)
dt = t[1] - t[0]  # Delta time (s)

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
u_curr[0] = 0.1  # Small displacement for the first atom


for cur_t in range(1, t_steps - 1):
    for cur_n in range(n):
        # Apply boundary conditions for an infinite solid
        if cur_n == 0:
            left = 0
            right = u_curr[cur_n + 1]
        elif cur_n == n - 1:
            left = u_curr[cur_n - 1]
            right = 0
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


# Animate or plot the displacement over time
plt.figure(figsize=(10, 6))
for i in range(0, t_steps, t_steps // 10):  # Plot a subset of time steps
    plt.plot(x, u_t[:, i], label=f"t = {i * dt:.2f}")
plt.xlabel("Atom Index")
plt.ylabel("Displacement")
plt.title("Wave Propagation in a Linear Chain with a Defect")
plt.legend(loc="upper right", fontsize=8)

# Perform Fourier Transform on the displacement of the defect atom
atom_to_analyze = defect_index
u_defect = u_t[atom_to_analyze, :]

# Apply FFT
fft_result_defect = np.fft.fft(u_defect)
fft_result_host = np.fft.fft(u_t[10])
frequencies = np.fft.fftfreq(t_steps, d=dt)
positive_frequencies = frequencies[frequencies >= 0]
fft_magnitude_guest = np.abs(fft_result_defect[:len(positive_frequencies)])
fft_magnitude_host = np.abs(fft_result_host[:len(positive_frequencies)])

# Normalize FFT result
fft_magnitude_guest /= np.max(fft_magnitude_guest)
fft_magnitude_host /= np.max(fft_magnitude_host)

# Plot the results
plt.figure(figsize=(10, 6))

# Displacement plot
plt.subplot(2, 1, 1)
plt.plot(t, u_defect, label="Displacement of Defect Atom")
plt.plot(t, u_t[10], label="Displacement of guest Atom")
plt.xlabel("Time")
plt.ylabel("Displacement")
plt.title("Displacement vs Time")
plt.legend()

# Fourier Transform plot
plt.subplot(2, 1, 2)
plt.plot(positive_frequencies, fft_magnitude_guest, label="FFT Spectrum guest")
plt.plot(positive_frequencies, fft_magnitude_host, label="FFT Spectrum host")
plt.xlabel("Frequency")
plt.ylabel("Amplitude (Normalized)")
plt.title("Frequency Spectrum (Fourier Transform)")
plt.legend()

plt.tight_layout()
plt.show()
