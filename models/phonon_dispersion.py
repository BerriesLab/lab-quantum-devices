import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# Parameters
N = 1000  # Number of atoms
guest_index = 50  # Index of the guest atom
k_host = 1.0  # Harmonic spring constant for host atoms
k_guest = 2.0  # Harmonic constant for guest atom
alpha_guest = 0.1  # Cubic anharmonic constant for guest
beta_guest = 0.05  # Quartic anharmonic constant for guest


# Equations of motion
def equations_of_motion(t, y):
    u = y[:N]  # Displacements of atoms
    v = y[N:]  # Velocities of atoms

    dudt = v  # Velocity to compute
    dvdt = np.zeros(N)  # Accelerations to compute

    # Host atoms: harmonic interactions
    for i in range(1, N - 1):
        if i == guest_index:
            continue
        dvdt[i] = k_host * (u[i + 1] - 2 * u[i] + u[i - 1])

    # Guest atom: harmonic + anharmonic terms
    dvdt[guest_index] = (
            k_guest * (u[guest_index + 1] - 2 * u[guest_index] + u[guest_index - 1])
            + alpha_guest * (u[guest_index] ** 3)
            + beta_guest * (u[guest_index] ** 4)
    )

    # Boundary conditions (e.g., fixed ends)
    dvdt[0] = 0
    dvdt[N - 1] = 0

    return np.concatenate([dudt, dvdt])


def calculate_fourier_transform(u_sol):
    # Create an array to store the phonon frequencies for each wavevector
    k_values = np.linspace(-np.pi, np.pi, N)  # Wave vectors in the 1D chain (for simplicity)
    frequencies = []
    # Loop over wave vectors
    for k in k_values:
        phonon_frequencies = []

        # Loop over atoms
        for i in range(N):
            # Take the Fourier transform of the displacement for atom i
            u_i = u_sol[i, :]  # Displacement for atom i over time
            u_i_fft = np.fft.fft(u_i)  # Fourier transform
            # Calculate the frequency from the FFT result
            freq = np.fft.fftfreq(len(t_eval), (t_eval[1] - t_eval[0]))

            # Find the peak frequency for the corresponding k (the frequency of the mode)
            phonon_frequencies.append(np.abs(u_i_fft[int(k * N / (2 * np.pi))]))  # Pick the corresponding frequency

        frequencies.append(phonon_frequencies)

    # Plotting the dispersion relation (ω vs k)
    plt.plot(k_values, frequencies)
    plt.xlabel('Wave vector (k)')
    plt.ylabel('Frequency (ω)')
    plt.title('Phonon Dispersion Relation')
    plt.show()


# Initial conditions
u0 = np.zeros(N)  # Initial displacements
u0[guest_index] = 0.1  # Perturb guest atom slightly by 0.1
v0 = np.zeros(N)  # Initial velocities
y0 = np.concatenate([u0, v0])  # Combine displacements and velocities

# Time integration
t_span = (0, 1000)  # Start and end times
t_eval = np.linspace(0, 10000, 100000)  # Time points to evaluate
solution = solve_ivp(equations_of_motion, t_span, y0, t_eval=t_eval)

# Displacements over time
u_sol = solution.y[:N, :]  # Extract the displacement solutions

calculate_fourier_transform(u_sol)

# Plot the displacement of the guest atom and one host atom
plt.plot(t_eval, u_sol[guest_index, :], label="Guest Atom (Atom 50)")
plt.plot(t_eval, u_sol[10, :], label="Host Atom (Atom 10)")  # Example of a host atom
plt.xlabel("Time")
plt.ylabel("Displacement")
plt.legend()
plt.show()
