"""Bit-order helpers. Qiskit count strings are little-endian: the rightmost character is qubit 0.

Never index a count string by hand in a notebook; use to_x / from_x.
"""


def to_x(bitstring):
    """Count string 'q_{n-1}...q_0' -> list [x_0, ..., x_{n-1}].  Example: to_x('110') == [0, 1, 1]."""
    return [int(c) for c in str(bitstring).replace(" ", "")[::-1]]


def from_x(x):
    """List [x_0, ..., x_{n-1}] -> count string 'q_{n-1}...q_0'.  Example: from_x([0, 1, 1]) == '110'."""
    return "".join(str(int(v)) for v in list(x)[::-1])


def index_to_x(k, n):
    """Integer basis-state index -> [x_0..x_{n-1}] where x_i is qubit i.  Example: index_to_x(6, 3) == [0, 1, 1]."""
    return [(int(k) >> i) & 1 for i in range(n)]


def x_to_index(x):
    """Inverse of index_to_x.  Example: x_to_index([0, 1, 1]) == 6."""
    return sum(int(v) << i for i, v in enumerate(x))


def phase_from_counts(counts, m):
    """QPE counts on m evaluation qubits (qubit i -> classical bit i) -> (phase of the most frequent outcome, its frequency).

    qiskit's phase_estimation has no final swaps, so the phase is int(string[::-1], 2) / 2**m.
    Example: phase_from_counts({'110': 4096}, 3) == (0.375, 1.0).
    """
    best = max(counts, key=counts.get)
    total = sum(counts.values())
    s = best.replace(" ", "")
    assert len(s) == m, f"expected {m} bits, got '{best}'; measure only the evaluation qubits"
    return int(s[::-1], 2) / 2 ** m, counts[best] / total
