"""Generate data/v2g_fleet.csv for notebook 10 (numpy only).

    python tools/generate_v2g_data.py            # writes data/v2g_fleet.csv
    python tools/generate_v2g_data.py --out FILE

80 synthetic cars, columns: soc, hours_norm, price, load, discharge.  The label comes from a simple rule that stands in for an
optimiser's decisions (the paper trains its model on solutions of approximate dynamic programming). It is not real fleet data.
"""
import argparse
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COLUMNS = ["soc", "hours_norm", "price", "load", "discharge"]


def make(n=80, seed=7):
    """Return the (n, 5) array: features then label (1 = discharge to the grid now)."""
    rng = np.random.default_rng(seed)
    soc = rng.uniform(0.1, 1.0, n)          # state of charge now
    hours = rng.uniform(0.5, 12, n)         # hours until the car leaves
    price = rng.uniform(0, 1, n)            # normalised electricity price now
    load = rng.uniform(0, 1, n)             # normalised local grid load now
    slack = hours * 0.1 - (0.8 - soc)       # spare charging time: can it still leave at 80%?
    y = ((slack > 0.25) & ((price + load) / 2 > 0.5)).astype(int)
    return np.c_[soc, hours / 12, price, load, y]


def main(path):
    """Write the CSV with 6 decimals and a header row."""
    data = make()
    with open(path, "w") as f:
        f.write(",".join(COLUMNS) + "\n")
        for row in data:
            f.write(",".join(f"{v:.6f}" for v in row[:4]) + f",{int(row[4])}\n")
    print(f"wrote {path}: {len(data)} rows, {int(data[:, 4].sum())} discharge ({data[:, 4].mean():.0%})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "..", "data", "v2g_fleet.csv"))
    main(ap.parse_args().out)
