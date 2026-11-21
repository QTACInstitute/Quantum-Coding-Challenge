# qff: the shared helpers

Pure Python, no notebook magic. `import qff` gives `qff.SEED` (2026) and the modules `bits`, `classical`, `day`, `plots`; `qff.quantum` and `qff.chem` load on first use (they import qiskit). Every function is short and has a docstring; read the source.

## `qff.bits`: bit order
Count strings are little-endian: the rightmost character is qubit 0. Never index them by hand.

| Function | One line | Example |
|---|---|---|
| `to_x(bitstring) -> list[int]` | count string to `[x_0, ..., x_{n-1}]` | `to_x("110") == [0, 1, 1]` |
| `from_x(x) -> str` | inverse of `to_x` | `from_x([0, 1, 1]) == "110"` |
| `index_to_x(k, n) -> list[int]` | basis-state index to x (bit i of k is qubit i) | `index_to_x(6, 3) == [0, 1, 1]` |
| `x_to_index(x) -> int` | inverse of `index_to_x` | `x_to_index([0, 1, 1]) == 6` |
| `phase_from_counts(counts, m) -> (phase, frequency)` | QPE: phase of the most frequent outcome, reading the string reversed | `phase_from_counts({"110": 4096}, 3) == (0.375, 1.0)` |

## `qff.classical`: baselines (run these first)
| Function | One line | Example |
|---|---|---|
| `brute_force(qp) -> (x, value, table)` | try all 2**n states of a `QuadraticProgram`; best feasible x, its value, and `table = [(x, value, feasible), ...]` sorted by value | `x, v, table = brute_force(qp)`; all optima: `[t[0] for t in table if t[2] and t[1] == v]` |
| `diag_of(op, offset=0.0) -> ndarray` | energy of every basis state for a Z-only `SparsePauliOp` (entry k: bit i of k is qubit i) | `diag = diag_of(cost_op, offset); diag.min()` |

## `qff.quantum`: Qiskit helpers
| Function | One line | Example |
|---|---|---|
| `sv_sampler(shots=4096)` | exact-statevector V2 sampler with the day's seed | `sv_sampler().run([qc]).result()[0].data.meas.get_counts()` |
| `sv_estimator()` | exact-statevector V2 estimator | `sv_estimator().run([(circuit, op)]).result()[0].data.evs` |
| `qaoa_energy(ansatz, diag) -> f` | `f(theta)` is the exact expected cost; theta order is alphabetical, all betas then all gammas | `f = qaoa_energy(qaoa_ansatz(cost_op, reps=1), diag); minimize(f, [0.5, 0.5], method="COBYLA")` |
| `top_states(circuit_or_probs, k=5)` | k likeliest states as `[(x-ordered string, probability)]` from a circuit, Statevector, dict or array | `top_states(qc.assign_parameters(theta), 3)` |
| `device_preview(circuit, n=None) -> dict` | transpile for a local pretend device: `depth`, `two_qubit_gates`, `size`, `num_qubits` | `device_preview(qc)["two_qubit_gates"]` |

## `qff.chem`: Hamiltonian files
| Function | One line | Example |
|---|---|---|
| `load_hamiltonian(path) -> Ham` | read a JSON from `data/`; `Ham` has `name, description, num_qubits, op, shift, hf_x_qubits, e_hf, e_exact, e_fci_full, generators, meta` | `ham = load_hamiltonian(f"{DATA}/h2_parity_0.735.json")`; total energy = eigenvalue of `ham.op` + `ham.shift` |

Hartree-Fock (or start) state: `qc.x(ham.hf_x_qubits)`. Energies are in Hartree; chemical accuracy is 1.6 mHa. For the site model (`site_model_*.json`), `e_fci_full` is `None`, `generators` is empty, `e_exact` is the ground energy in the one-up, one-down electron sector (the physical answer), and `meta["e_min_full_matrix"]` is the lowest eigenvalue of the whole 16x16 matrix (a 3-electron state: the trap notebook 8 teaches).

## `qff.plots`: small figures (each returns the Axes)
| Function | One line | Example |
|---|---|---|
| `plot_counts(probs, highlight=(), title="", ax=None)` | bar chart of `{string: probability}`, highlighted strings in red | `plot_counts(dict(top_states(qc, 8)), highlight=["010101"])` |
| `plot_convergence(history, exact=None, band=None, ax=None)` | line plot of optimiser values (list or dict of lists), dashed exact line, shaded band | `plot_convergence({"run 1": vals}, exact=-7.88107, band=(-7.88107, -7.87947))` |
| `show_image(arr, title="", ax=None)` | grey image without ticks | `show_image(img, "seismic section")` |
| `plot_flow(steps, loop=None, title="", ax=None)` | flow diagram of coloured boxes (`"source"`, `"move"`, `"store"`, `"use"` or a hex colour) with an optional return arrow | `plot_flow([("Circuit", "eq. 4-7", "use"), ("Optimiser", "COBYLA", "store")], loop=(1, 0, "new knobs"))` |
| `plot_landscape(f, x_range, y_range, n=41, ..., marks=(), cmap="viridis")` | heat map of `f(x, y)` on a grid, dark is low; `marks` are `(x, y, label, colour)` | `plot_landscape(lambda b, g: energy([b, g]), (0, np.pi), (0, np.pi), xlabel="beta", ylabel="gamma")` |
| `plot_cost_histogram(diag, dists, title="", ax=None)` | grouped bars: probability of landing on each cost value, one bar per distribution | `plot_cost_histogram(diag, {"guessing": np.full(64, 1/64), "p = 3": probs})` |
| `plot_phases(diag, gamma, title="", ax=None)` | polar picture of a QAOA cost layer: each cost value turned by `-gamma * cost` (needs a polar axes) | `plot_phases(diag, 0.3)` |
| `STOP_COLORS` | the four stop colours: teal (source), blue (move), purple (store), magenta (use) | `STOP_COLORS["move"]` |

## `qff.day`: the storyline
| Function | One line | Example |
|---|---|---|
| `show_day(stop=None, challenge=None)` | the four-stop map as HTML; stop lit, challenge ringed | `qff.day.show_day(stop=2, challenge=5)` |
| `STOPS`, `CHALLENGES`, `HEADINGS` | the data behind the map and the exact section headings | `qff.day.CHALLENGES[4]["label"]` |
| `header_md`, `section0_code`, `section5_md`, `section6_md`, `glossary_md`, `IBM_MD`, `IBM_PREVIEW_CODE`, `SETUP_CODE` | shared text for builders; used by `tools/nbkit.py` | `glossary_md(["VQE", "ansatz"])` |

## Self-test
`python -m qff.selftest` (from the repo root) checks the bit helpers, `brute_force`, the QPE phase reading, `diag_of` and `qaoa_energy` on the six-node vertex-cover ladder, the Hamiltonian loader and the stop map.
