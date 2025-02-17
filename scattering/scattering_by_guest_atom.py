import numpy as np
import matplotlib.pyplot as plt


def phonon_dispersion(chain_length, defect_positions=None, defect_strengths=None, defect_types=None):
    """
    Calculate and plot the phonon dispersion relation for a linear chain of atoms with optional defects.

    Parameters:
    chain_length (int): Number of atoms in the chain.
    defect_positions (list of int, optional): Positions of defects in the chain (0-indexed).
    defect_strengths (list of float, optional): Strengths of defects (e.g., mass or spring constant modifications).
    defect_types (list of str, optional): Types of defects ("mass" or "spring").
    """
    # Constants
    k = 1.0  # Spring constant (default)
    m = 1.0  # Mass of atoms (default)

    # Arrays for masses and spring constants
    masses = np.full(chain_length, m)
    spring_constants = np.full(chain_length - 1, k)

    # Apply defects
    if defect_positions:
        for i, pos in enumerate(defect_positions):
            if defect_types[i] == "mass":
                masses[pos] = defect_strengths[i]  # Modify mass at the defect position
            elif defect_types[i] == "spring":
                if pos > 0:
                    spring_constants[pos - 1] = defect_strengths[i]  # Modify spring constant between atoms

    # Matrix setup for the equations of motion
    # This is the dynamical matrix
    H = np.zeros((chain_length, chain_length))

    for i in range(chain_length):
        if i > 0:
            H[i, i - 1] = -np.sqrt(k / masses[i])  # Coupling to previous atom
        if i < chain_length - 1:
            H[i, i + 1] = -np.sqrt(k / masses[i])  # Coupling to next atom
        H[i, i] = 2 * np.sqrt(k / masses[i])  # Diagonal term

    # Solve the eigenvalue problem (find eigenfrequencies)
    eigenvalues, eigenvectors = np.linalg.eig(H)

    # Sort the eigenfrequencies in ascending order
    eigenfrequencies = np.sqrt(np.abs(eigenvalues))

    # Return eigenfrequencies (phonon dispersion relation)
    return eigenfrequencies


def plot_dispersion_relation(chain_length, defect_positions=None, defect_strengths=None, defect_types=None):
    # Calculate the phonon dispersion relation
    frequencies = phonon_dispersion(chain_length, defect_positions, defect_strengths, defect_types)

    # Plot the dispersion relation
    k_values = np.linspace(0, np.pi, 100)  # k values from 0 to pi for the dispersion
    plt.figure(figsize=(8, 6))
    plt.plot(k_values, frequencies, label="Phonon Dispersion")
    plt.xlabel("Wavevector (k)")
    plt.ylabel("Frequency (ω)")
    plt.title("Phonon Dispersion Relation with Defects")
    plt.grid(True)
    plt.legend()
    plt.show()


# Example usage
chain_length = 20  # Number of atoms in the chain
defect_positions = []  # Positions of defects (0-indexed)
defect_strengths = []  # Mass or spring constant modifications at defects
defect_types = ["mass", "spring"]  # Defect types: "mass" or "spring"

plot_dispersion_relation(chain_length, defect_positions, defect_strengths, defect_types)