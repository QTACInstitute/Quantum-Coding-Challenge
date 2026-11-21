"""Load the shipped Hamiltonian JSON files (data/*.json). Students never need qiskit-nature or pyscf."""
import json
from dataclasses import dataclass, field

from qiskit.quantum_info import SparsePauliOp


@dataclass
class Ham:
    """A qubit Hamiltonian. Energies in Hartree; total energy = eigenvalue of `op` + `shift`.

    hf_x_qubits: apply X on these qubits to get the starting state (Hartree-Fock, or the site model's start state).
    e_fci_full is None for the site model; generators are empty there. `meta` keeps every other JSON field.
    """
    name: str
    description: str
    num_qubits: int
    op: SparsePauliOp
    shift: float
    hf_x_qubits: list
    e_hf: float
    e_exact: float
    e_fci_full: float
    generators: list = field(default_factory=list)
    meta: dict = field(default_factory=dict)


def _op(paulis, coeffs):
    """Labels and real coefficients -> SparsePauliOp."""
    return SparsePauliOp(paulis, coeffs=[complex(c) for c in coeffs])


def load_hamiltonian(path):
    """Read a Hamiltonian JSON file -> Ham.  Example: ham = load_hamiltonian(f'{DATA}/lih_parity_1.6.json'); ham.op.num_qubits == 4."""
    with open(path) as f:
        d = json.load(f)
    known = ("name", "description", "num_qubits", "paulis", "coeffs", "shift", "hf_x_qubits", "e_hf", "e_exact",
             "e_fci_full", "generators")
    return Ham(d["name"], d["description"], d["num_qubits"], _op(d["paulis"], d["coeffs"]), d["shift"],
               list(d["hf_x_qubits"]), d["e_hf"], d["e_exact"], d["e_fci_full"],
               [_op(g["paulis"], g["coeffs"]) for g in d["generators"]],
               {k: v for k, v in d.items() if k not in known})
