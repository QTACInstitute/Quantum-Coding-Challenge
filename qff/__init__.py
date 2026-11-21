"""qff: small shared helpers for the KACST Qiskit Fall Fest 2026 notebooks.

Pure Python, no notebook magic. Read any file here; each function is short on purpose.
Modules: day (section 0 map), bits (bit order), classical (baselines), quantum (primitives, QAOA energy),
chem (Hamiltonian files), plots (small figures).  See qff/README.md for a one-line example per function.

Import the submodules you need, e.g.  from qff import bits, classical  (import qff alone gives SEED and the submodules).
"""
__version__ = "0.1.0"
__author__ = "Ahmed Elghadban, Quantumy"
SEED = 2026   # one seed for the whole day

from . import bits, classical, day, plots  # noqa: E402,F401  (light imports only; quantum and chem load qiskit lazily)


def __getattr__(name):
    """Load qff.quantum and qff.chem on first use (they import qiskit)."""
    if name in ("quantum", "chem"):
        import importlib
        return importlib.import_module(f"qff.{name}")
    raise AttributeError(name)
