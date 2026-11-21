"""Generate the molecular Hamiltonian JSON files in data/ (ours only: needs qiskit-nature and pyscf).

    python tools/generate_chemistry.py            # writes data/lih_parity_*.json and data/h2_parity_*.json
    python tools/generate_chemistry.py --out DIR  # write somewhere else (used by run_tests.py to check determinism)

Students never run this. They read the JSON files with qff.chem.load_hamiltonian.
Energies are in Hartree (Ha). Chemical accuracy = 1.6 mHa.
"""
import argparse
import json
import os
import warnings

import numpy as np

warnings.filterwarnings("ignore")

LIH_R = [1.2, 1.4, 1.6, 1.8, 2.0, 2.4, 3.0]
H2_R = [0.5, 0.6, 0.735, 0.9, 1.2, 1.6]
HERE = os.path.dirname(os.path.abspath(__file__))


def versions():
    """Package versions recorded in every file."""
    import pyscf, qiskit, qiskit_nature
    return {"qiskit": qiskit.__version__, "qiskit_nature": qiskit_nature.__version__, "pyscf": pyscf.__version__}


def full_fci(atom, basis="sto3g"):
    """Total energy (Ha) of the whole molecule: PySCF FCI in the full basis, no active-space cut."""
    from pyscf import fci, gto, scf
    mol = gto.M(atom=atom, basis=basis, verbose=0)
    mf = scf.RHF(mol).run()
    return float(fci.FCI(mf).kernel()[0])


def pauli_dict(op):
    """SparsePauliOp with real coefficients -> sorted {'paulis': [...], 'coeffs': [...]} (asserts imaginary parts are 0)."""
    assert np.abs(op.coeffs.imag).max() < 1e-12, "complex coefficients"
    pairs = sorted(zip((p.to_label() for p in op.paulis), (float(c) for c in op.coeffs.real)))   # sorted: reruns identical
    return {"paulis": [p for p, _ in pairs], "coeffs": [c for _, c in pairs]}


def build(name, atom, R, active, orbitals, description):
    """Build one Hamiltonian record: map to qubits, check Hartree-Fock and the exact energy against FCI."""
    from qiskit.quantum_info import Statevector
    from qiskit_nature.second_q.circuit.library import UCCSD, HartreeFock
    from qiskit_nature.second_q.drivers import PySCFDriver
    from qiskit_nature.second_q.mappers import ParityMapper
    from qiskit_nature.second_q.transformers import ActiveSpaceTransformer
    prob = PySCFDriver(atom=atom, basis="sto3g").run()
    act = ActiveSpaceTransformer(active[0], active[1], active_orbitals=orbitals).transform(prob)
    mapper = ParityMapper(num_particles=act.num_particles)
    op = mapper.map(act.hamiltonian.second_q_op()).simplify()
    shift = float(sum(act.hamiltonian.constants.values()))
    hf = HartreeFock(act.num_spatial_orbitals, act.num_particles, mapper)
    gens = list(UCCSD(act.num_spatial_orbitals, act.num_particles, mapper, initial_state=hf).operators)
    k = int(np.argmax(Statevector(hf).probabilities()))          # HF is a basis state: bit i of k is qubit i
    hf_x = [i for i in range(op.num_qubits) if (k >> i) & 1]
    e_hf = float(Statevector(hf).expectation_value(op).real) + shift
    e_exact = float(np.linalg.eigvalsh(op.to_matrix())[0]) + shift
    e_fci = full_fci(atom)
    assert abs(e_hf - float(prob.reference_energy)) < 1e-6, f"HF mismatch {e_hf} vs {prob.reference_energy}"
    assert e_fci - 1e-8 <= e_exact <= e_hf + 1e-8, f"{name}: exact energy {e_exact} not between FCI {e_fci} and HF {e_hf}"
    rec = {"name": name, "description": description, "geometry": {"atom": atom, "unit": "angstrom", "R": R},
           "basis": "sto3g", "active_space": {"electrons": active[0], "spatial_orbitals": active[1], "orbitals": orbitals},
           "mapping": "parity, two-qubit reduction", "num_qubits": int(op.num_qubits)}
    rec.update(pauli_dict(op))
    rec.update({"shift": shift, "hf_x_qubits": hf_x, "e_hf": e_hf, "e_exact": e_exact, "e_fci_full": e_fci,
                "generators": [pauli_dict(g) for g in gens], "generated_with": versions()})
    return rec


def clean(x):
    """Round floats to 10 decimals (removes 1e-16 SCF noise, so reruns are byte-identical) and turn -0.0 into 0.0."""
    if isinstance(x, float):
        return round(x, 10) + 0.0
    if isinstance(x, list):
        return [clean(v) for v in x]
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    return x


def write(rec, path):
    """Write JSON with fixed formatting so regenerated files are byte-identical."""
    with open(path, "w") as f:
        json.dump(clean(rec), f, indent=1)
        f.write("\n")


def main(out):
    """Write all LiH and H2 files into the folder `out`."""
    os.makedirs(out, exist_ok=True)
    for R in LIH_R:
        rec = build(f"LiH R={R}", f"Li 0 0 0; H 0 0 {R}", R, (2, 3), [1, 2, 5],
                    "Lithium hydride, STO-3G, 2 electrons in 3 orbitals (orbitals 1, 2, 5), parity-mapped to 4 qubits.")
        write(rec, os.path.join(out, f"lih_parity_{R}.json"))
        print(f"LiH R={R}: HF {rec['e_hf']:.5f}  exact {rec['e_exact']:.5f}  FCI {rec['e_fci_full']:.5f}  terms {len(rec['paulis'])}")
    for R in H2_R:
        rec = build(f"H2 R={R}", f"H 0 0 0; H 0 0 {R}", R, (2, 2), None,
                    "Hydrogen molecule, STO-3G, the whole molecule (2 electrons, 2 orbitals), parity-mapped to 2 qubits.")
        write(rec, os.path.join(out, f"h2_parity_{R}.json"))
        print(f"H2 R={R}: HF {rec['e_hf']:.5f}  exact {rec['e_exact']:.5f}  FCI {rec['e_fci_full']:.5f}  terms {len(rec['paulis'])}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "data"))
    main(ap.parse_args().out)
