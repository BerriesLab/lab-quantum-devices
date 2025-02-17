from ase import Atoms
from ase.visualize import view
from ase.calculators.espresso import Espresso
from phonopy import Phonopy
# from phonopy.interface.ase import get_displacements

# Distance between atoms (in angstrom)
a = 1.42  # Example for C-C

n_atoms = 100
linear_atomic_chain = Atoms('C' * n_atoms, positions=[(i * a, 0, 0) for i in range(n_atoms)])
# linear_atomic_chain_with_1_defect[49].symbol = 'N'
linear_atomic_chain.write('linear_atomic_chain_with_1_defect.xyz')
view(linear_atomic_chain)

# Set calculator
qe_input = {
    'pw': '/Applications/qe-6.8/bin/pw.x',  # Path to Quantum Espresso pw.x
    'parallel': True  # Whether to run in parallel
}
calc = Espresso(
    pseudopotentials={'C': 'C.pz-n-rrkjus.UPF', 'N': 'N.pz-n-rrkjus.UPF'},
    tstress=True,
    tprnfor=True,
    kpts=(4, 4, 4))
linear_atomic_chain.set_calculator(calc)
linear_atomic_chain.get_potential_energy()
linear_atomic_chain.write('linear_atomic_chain_with_1_defect_relaxed.xyz')
view(linear_atomic_chain)

# Calculate phonon dispersion relation
# displacements = get_displacements(linear_atomic_chain_with_1_defect, 0.01)



