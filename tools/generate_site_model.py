"""Generate the two-orbital donor-acceptor model Hamiltonians for notebook 8 (needs qiskit-nature only).

    python tools/generate_site_model.py            # writes data/site_model_R*.json and data/site_model_far.json
    python tools/generate_site_model.py --out DIR

THE PARAMETERS ARE INVENTED FOR TEACHING. This is not an ab initio MOF calculation (see the plan, decision 1).
Orbital C = filled CO2 lone-pair orbital (donor), orbital M = empty orbital on the framework's open metal site.
Spin orbitals are ordered [C_up, M_up, C_down, M_down] = qubits 0..3 (Jordan-Wigner).  Energies in Hartree, R in Angstrom.

    H(R) = sum_s [ eC n_Cs + eM n_Ms - t(R) (c+_Cs c_Ms + h.c.) ] + UC n_C,up n_C,down + UM n_M,up n_M,down
    t(R) = 0.15 exp(-(R-2)/0.5)      V(R) = 0.05 exp(-(R-2)/0.15)      E0(far) = 2 eC + UC = -1.5
"""
import argparse
import json
import os
import warnings

import numpy as np

warnings.filterwarnings("ignore")

EC, EM, UC, UM = -0.9, -0.2, 0.3, 0.5
R_LIST = [1.8, 1.9, 2.0, 2.1, 2.2, 2.4, 2.8, 3.5]
HERE = os.path.dirname(os.path.abspath(__file__))
INIT_X = [0, 2]          # both electrons on the CO2 orbital: C_up and C_down


def hopping(R):
    """Orbital overlap t(R) in Ha; R=None means 'far away' (t = 0)."""
    return 0.0 if R is None else 0.15 * np.exp(-(R - 2.0) / 0.5)


def repulsion(R):
    """Classical repulsion V(R) in Ha from 'everything else'; zero far away."""
    return 0.0 if R is None else 0.05 * np.exp(-(R - 2.0) / 0.15)


def model_op(t):
    """Jordan-Wigner SparsePauliOp (4 qubits) of the model for hopping t."""
    from qiskit_nature.second_q.mappers import JordanWignerMapper
    from qiskit_nature.second_q.operators import FermionicOp
    terms = {"+_0 -_0": EC, "+_1 -_1": EM, "+_2 -_2": EC, "+_3 -_3": EM,
             "+_0 -_0 +_2 -_2": UC, "+_1 -_1 +_3 -_3": UM}
    if t != 0.0:
        terms.update({"+_0 -_1": -t, "+_1 -_0": -t, "+_2 -_3": -t, "+_3 -_2": -t})
    return JordanWignerMapper().map(FermionicOp(terms, num_spin_orbitals=4)).simplify()


def sector_ground(op):
    """Lowest eigenvalue among states with one spin-up and one spin-down electron (qubits {0,1} and {2,3})."""
    keep = [k for k in range(16) if ((k & 1) + ((k >> 1) & 1)) == 1 and (((k >> 2) & 1) + ((k >> 3) & 1)) == 1]
    m = op.to_matrix()[np.ix_(keep, keep)]
    return float(np.linalg.eigvalsh(m)[0])


def build(R):
    """One JSON record. R=None is the far-away geometry."""
    from qiskit.quantum_info import Statevector
    from qiskit import QuantumCircuit
    t = float(hopping(R))
    op = model_op(t)
    assert np.abs(op.coeffs.imag).max() < 1e-12
    init = QuantumCircuit(4)
    init.x(INIT_X)
    e_init = float(Statevector(init).expectation_value(op).real)
    e_sector = sector_ground(op)
    pairs = sorted(zip((p.to_label() for p in op.paulis), (float(c) for c in op.coeffs.real)))
    label = "far" if R is None else f"R={R}"
    rec = {"name": f"CO2 site model {label}",
           "description": "Invented two-orbital donor-acceptor model of CO2 on an open metal site (teaching model, not ab initio). "
                          "Two electrons; Jordan-Wigner, spin orbitals [C_up, M_up, C_down, M_down]. "
                          "e_exact is the ground energy in the one-up, one-down sector (the physical answer); "
                          "e_min_full_matrix is the lowest eigenvalue of the whole 16x16 matrix, which belongs to a 3-electron state.",
           "geometry": {"R": R, "unit": "angstrom"}, "basis": "model", "active_space": {"electrons": 2, "spatial_orbitals": 2},
           "mapping": "jordan-wigner", "num_qubits": 4,
           "paulis": [p for p, _ in pairs], "coeffs": [c for _, c in pairs],
           "shift": 0.0, "hf_x_qubits": INIT_X, "init_x_qubits": INIT_X, "e_hf": e_init, "e_exact": e_sector,
           "e_fci_full": None, "e_exact_sector": e_sector, "e_min_full_matrix": float(np.linalg.eigvalsh(op.to_matrix())[0]),
           "t": t, "V": float(repulsion(R)), "R": R, "generators": [], "generated_with": versions()}
    rec["binding_incl_V_mHa"] = None
    return rec


def versions():
    """Package versions recorded in every file."""
    import qiskit, qiskit_nature
    return {"qiskit": qiskit.__version__, "qiskit_nature": qiskit_nature.__version__}


def clean(x):
    """Round floats to 10 decimals and turn -0.0 into 0.0 so reruns are byte-identical."""
    if isinstance(x, float):
        return round(x, 10) + 0.0
    if isinstance(x, list):
        return [clean(v) for v in x]
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    return x


def main(out):
    """Write one file per geometry plus the far-away file; print the binding table."""
    os.makedirs(out, exist_ok=True)
    far = build(None)
    assert abs(far["e_exact"] - (-1.5)) < 1e-12, "far geometry must be exactly 2 eC + UC"
    recs = [(f"site_model_R{R}.json", build(R)) for R in R_LIST] + [("site_model_far.json", far)]
    for fname, rec in recs:
        b = (rec["e_exact"] + rec["V"] - far["e_exact"]) * 1000
        rec["binding_incl_V_mHa"] = b
        with open(os.path.join(out, fname), "w") as f:
            json.dump(clean(rec), f, indent=1)
            f.write("\n")
        print(f"{fname:24s} t={rec['t']:.4f} E0={rec['e_exact']:.5f} full-matrix min={rec['e_min_full_matrix']:.4f} "
              f"V={rec['V']:.5f} binding={b:+.1f} mHa  terms={len(rec['paulis'])}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "data"))
    main(ap.parse_args().out)
