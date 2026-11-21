"""Classical baselines. They run first in every notebook."""
import numpy as np

from .bits import index_to_x


def brute_force(qp):
    """Try every x for a QuadraticProgram -> (best feasible x, its value, table).

    table = list of (x, value, feasible) for all 2**n states, sorted by value (ties in index order).
    Example: x, v, table = brute_force(qp);  optima = [t[0] for t in table if t[2] and t[1] == v].
    """
    n = qp.get_num_vars()
    rows = []
    for k in range(2 ** n):
        x = index_to_x(k, n)
        rows.append((x, float(qp.objective.evaluate(x)), bool(qp.is_feasible(x))))
    rows.sort(key=lambda r: r[1])
    best = next(r for r in rows if r[2])
    return best[0], best[1], rows


def diag_of(op, offset=0.0):
    """Real diagonal of a Z-only SparsePauliOp plus offset; entry k is the energy of basis state k (bit i of k = qubit i).

    Example: diag = diag_of(cost_op, offset); diag.min() is the best cost.
    """
    d = np.asarray(op.to_matrix(sparse=True).diagonal())
    assert np.abs(d.imag).max() < 1e-9, "operator has complex diagonal"
    return d.real + offset
