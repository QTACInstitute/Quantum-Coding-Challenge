"""Qiskit helpers: primitives, exact QAOA energy, state listing, and a pretend-device preview."""
import numpy as np
from qiskit.quantum_info import Statevector

from . import SEED
from .bits import from_x, index_to_x


def sv_sampler(shots=4096):
    """Exact-statevector V2 sampler with the day's seed.  Example: sv_sampler().run([qc]).result()[0].data.meas.get_counts()."""
    from qiskit.primitives import StatevectorSampler
    return StatevectorSampler(seed=SEED, default_shots=shots)


def sv_estimator():
    """Exact-statevector V2 estimator.  Example: sv_estimator().run([(circuit, observable)]).result()[0].data.evs."""
    from qiskit.primitives import StatevectorEstimator
    return StatevectorEstimator()


def qaoa_energy(ansatz, diag):
    """Return f(theta) = <C> computed exactly as probabilities @ diag.

    theta follows ansatz.parameters order, which is alphabetical: all betas first, then all gammas.
    Example: f = qaoa_energy(qaoa_ansatz(cost_op, reps=1), diag); f([0.5, 0.5]).
    """
    def f(theta):
        probs = Statevector(ansatz.assign_parameters(list(theta))).probabilities()
        return float(probs @ diag)
    return f


def top_states(circuit_or_probs, k=5):
    """The k most likely basis states as [(x-ordered string, probability)], most likely first.

    Accepts a circuit with no free parameters, a Statevector, a counts/probability dict, or a probability array.
    The string is x-ordered: character i is x_i (qubit i).  Example: top_states(qc, 3) -> [('010101', 0.51), ...].
    """
    obj = circuit_or_probs
    if hasattr(obj, "num_qubits") and not isinstance(obj, Statevector):
        obj = Statevector(obj)
    if isinstance(obj, Statevector):
        obj = obj.probabilities_dict()
    if not isinstance(obj, dict):
        arr = np.asarray(obj, dtype=float)
        n = int(np.log2(len(arr)))
        obj = {from_x(index_to_x(i, n)): p for i, p in enumerate(arr)}
    total = float(sum(obj.values()))
    items = sorted(obj.items(), key=lambda kv: -kv[1])[:k]
    return [("".join(str(b) for b in _x_of(key)), float(v) / total) for key, v in items]


def _x_of(key):
    """Count-string key -> x list (little-endian reversal)."""
    return [int(c) for c in str(key).replace(" ", "")[::-1]]


def device_preview(circuit, n=None):
    """Transpile for a local pretend device (GenericBackendV2) -> dict(depth, two_qubit_gates, size, num_qubits).

    Example: device_preview(qc)['two_qubit_gates'].  Nothing is sent anywhere; no account is needed.
    """
    from qiskit.providers.fake_provider import GenericBackendV2
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    backend = GenericBackendV2(num_qubits=max(n or 0, circuit.num_qubits), seed=SEED)
    isa = generate_preset_pass_manager(optimization_level=1, backend=backend, seed_transpiler=SEED).run(circuit)
    ops = isa.count_ops()
    two = sum(c for g, c in ops.items() if g in ("cx", "cz", "ecr", "swap"))
    return {"depth": isa.depth(), "two_qubit_gates": two, "size": isa.size(), "num_qubits": circuit.num_qubits}
