"""Unit-level self-tests for qff.   Run from the repo root:  python -m qff.selftest"""
import os
import warnings

import numpy as np

warnings.filterwarnings("ignore")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def test_bits():
    """to_x / from_x round-trip; index helpers agree with Qiskit order."""
    from qff import bits
    assert bits.to_x("110") == [0, 1, 1] and bits.from_x([0, 1, 1]) == "110"
    for s in ("0", "1", "0101", "111000"):
        assert bits.from_x(bits.to_x(s)) == s
    assert bits.index_to_x(6, 3) == [0, 1, 1] and bits.x_to_index([0, 1, 1]) == 6


def test_brute_force():
    """brute_force on a 3-variable program with a constraint."""
    from qiskit_optimization import QuadraticProgram
    from qff.classical import brute_force
    qp = QuadraticProgram()
    for v in "abc":
        qp.binary_var(v)
    qp.minimize(linear={"a": -3, "b": -2, "c": -1}, quadratic={("a", "b"): 4})
    qp.linear_constraint({"a": 1, "b": 1, "c": 1}, "==", 2, "two")
    x, val, table = brute_force(qp)
    assert x == [1, 0, 1] and val == -4 and len(table) == 8 and sum(t[2] for t in table) == 3, (x, val)
    assert table[0][1] <= table[-1][1]


def test_phase_warmup():
    """3-bit QPE warm-up: raw string '110' must read as 0.375."""
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import PhaseGate, phase_estimation
    from qff.bits import phase_from_counts
    from qff.quantum import sv_sampler
    qc = QuantumCircuit(4, 3)
    qc.x(3)
    qc.compose(phase_estimation(3, PhaseGate(2 * np.pi * 0.375)), inplace=True)
    qc.measure(range(3), range(3))
    counts = sv_sampler(1024).run([qc]).result()[0].data.c.get_counts()
    assert list(counts) == ["110"], counts
    assert phase_from_counts(counts, 3) == (0.375, 1.0)


def test_qaoa_energy():
    """Vertex-cover ladder: diag min 3, mean 6.5; energy at theta=0 equals the mean (uniform state)."""
    from qiskit.circuit.library import qaoa_ansatz
    from qiskit_optimization.applications import VertexCover
    from qiskit_optimization.converters import QuadraticProgramToQubo
    import networkx as nx
    from qff.classical import brute_force, diag_of
    from qff.quantum import qaoa_energy, top_states
    G = nx.Graph([(0, 1), (1, 2), (0, 3), (1, 4), (2, 5), (3, 4), (4, 5)])
    qp = VertexCover(G).to_quadratic_program()
    x, val, table = brute_force(qp)
    assert val == 3 and sum(1 for t in table if t[2]) == 17
    cost_op, offset = QuadraticProgramToQubo(penalty=2).convert(qp).to_ising()
    diag = diag_of(cost_op, offset)
    assert abs(diag.min() - 3.0) < 1e-9 and abs(diag.mean() - 6.5) < 1e-9
    ans = qaoa_ansatz(cost_op, reps=1)
    f = qaoa_energy(ans, diag)
    assert abs(f([0.0, 0.0]) - 6.5) < 1e-9
    from scipy.optimize import minimize
    res = minimize(f, x0=np.full(2, 0.5), method="COBYLA", options={"maxiter": 300})
    assert abs(res.fun - 4.565) < 0.01, res.fun          # plan: p=1, first start
    top = top_states(ans.assign_parameters(res.x), 3)
    assert len(top) == 3 and abs(sum(p for _, p in top)) <= 1.0 + 1e-9 and len(top[0][0]) == 6


def test_chem_and_day():
    """Shipped Hamiltonians load; H2 and LiH numbers; the stop map renders."""
    from qiskit.quantum_info import Statevector
    from qiskit import QuantumCircuit
    from qff.chem import load_hamiltonian
    from qff.day import show_day
    ham = load_hamiltonian(os.path.join(ROOT, "data", "lih_parity_1.6.json"))
    qc = QuantumCircuit(4)
    qc.x(ham.hf_x_qubits)
    e = Statevector(qc).expectation_value(ham.op).real + ham.shift
    assert ham.op.num_qubits == 4 and len(ham.generators) == 8 and abs(e - ham.e_hf) < 1e-8
    assert abs(np.linalg.eigvalsh(ham.op.to_matrix())[0] + ham.shift - ham.e_exact) < 1e-8
    h2 = load_hamiltonian(os.path.join(ROOT, "data", "h2_parity_0.735.json"))
    assert abs(h2.e_exact - (-1.13730604)) < 1e-6 and abs(h2.shift - 0.71996899) < 1e-6
    assert "المنبع" in show_day(1, 2).data and "font-weight:700" in show_day(1, 2).data


def test_teaching_plots():
    """The teaching figures draw without error on tiny inputs and return their axes (headless backend)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from qff import plots
    diag = np.array([2.0, 1.0, 1.0, 2.0])
    ax = plots.plot_flow([("a", "first", "source"), ("b", "second", "#0F62FE")], loop=(1, 0, "again"), title="t")
    assert len(ax.patches) == 2
    ax = plots.plot_landscape(lambda x, y: x + y, (0, 1), (0, 1), n=5, marks=[(0.5, 0.5, "best", "use")])
    assert ax.get_xlabel() == "" and len(ax.images) == 1
    ax = plots.plot_cost_histogram(diag, {"guess": np.full(4, 0.25), "tuned": np.array([0, 0.5, 0.5, 0])})
    assert len(ax.patches) == 4                                   # 2 cost levels x 2 distributions
    ax = plots.plot_phases(diag, 0.7)
    assert ax.name == "polar"
    axes = plots.plot_amplitude_stages({"a": np.array([0.0, 0.0, 1.0, 0.0]), "b": np.array([0.5, -0.5, 0.5, 0.5])}, suptitle="s")
    assert len(axes) == 2 and len(axes[0].patches) == 4
    axes = plots.plot_amplitude_stages({"a": np.full(4, 0.5), "b": np.array([0.5, 0.5, 0.5, -0.5])}, highlight=[3], labels=("not marked", "marked"))
    assert len(axes) == 2
    ax = plots.plot_grover_geometry(np.arcsin(0.5), steps=2)
    assert ax.get_ylabel() == "marked"
    plt.close("all")


def main():
    """Run every test and print one line each."""
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"ok  {name}")
    print("qff selftest passed")


if __name__ == "__main__":
    main()
