"""Small matplotlib helpers. Each returns the Axes so you can add a title, a line or a label."""
import matplotlib.pyplot as plt
import numpy as np


def plot_counts(probs, highlight=(), title="", ax=None):
    """Bar chart of {x-ordered string: probability}; strings in `highlight` are drawn in red.

    Example: plot_counts(dict(top_states(qc, 8)), highlight=['010101'], title='QAOA p=3').
    """
    ax = ax or plt.subplots(figsize=(7, 3))[1]
    keys = list(probs)
    ax.bar(range(len(keys)), [probs[k] for k in keys], color=["#FA4D56" if k in highlight else "#0F62FE" for k in keys])
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(keys, rotation=60, ha="right", fontfamily="monospace")
    ax.set_ylabel("probability")
    ax.set_title(title)
    return ax


def plot_convergence(history, exact=None, band=None, ax=None):
    """Line plot of optimiser values; `history` is a list of values or a dict {label: list}.

    exact draws a dashed line; band=(lo, hi) shades a region (e.g. chemical accuracy).
    Example: plot_convergence({'run 1': vals}, exact=-7.88107, band=(-7.88107, -7.87947)).
    """
    ax = ax or plt.subplots(figsize=(7, 3.5))[1]
    runs = history if isinstance(history, dict) else {"run": history}
    for label, vals in runs.items():
        ax.plot(vals, label=label)
    if exact is not None:
        ax.axhline(exact, ls="--", color="k", label="exact")
    if band is not None:
        ax.axhspan(band[0], band[1], color="#24A148", alpha=0.2)
    ax.set_xlabel("evaluation")
    ax.set_ylabel("value")
    ax.legend()
    return ax


def show_image(arr, title="", ax=None):
    """Show a 2-D array as a grey image without axes ticks.  Example: show_image(img, 'seismic section')."""
    ax = ax or plt.subplots(figsize=(3, 3))[1]
    ax.imshow(np.asarray(arr), cmap="gray")
    ax.set_title(title)
    ax.set_xticks([])
    ax.set_yticks([])
    return ax


# ---------------------------------------------------------------------------------------------------------------------
# Teaching figures (added for the self-contained notebooks). Colours follow the four stops of the day.
# ---------------------------------------------------------------------------------------------------------------------
STOP_COLORS = {"source": "#007D79", "move": "#0F62FE", "store": "#8A3FFC", "use": "#D02670"}   # teal, blue, purple, magenta
GREYS = ["#8D8D8D", "#78A9FF", "#0F62FE", "#002D9C", "#001141"]                                    # guessing, then deeper blues


def _colour(c):
    """A hex colour, or a key of STOP_COLORS."""
    return STOP_COLORS.get(c, c)


def plot_flow(steps, loop=None, title="", ax=None):
    """Draw a left-to-right flow diagram of coloured boxes joined by arrows.

    steps: list of (title, subtitle, colour); colour is a hex string or a key of STOP_COLORS ("source", "move", "store", "use").
    loop: optional (from_index, to_index, text) draws a return arrow under the boxes (e.g. the optimiser feeding the circuit).
    Example: plot_flow([("Hadamards", "equal mix", "source"), ("Cost layer", "phase", "move")], loop=(1, 0, "tune knobs")).
    """
    from matplotlib.patches import FancyBboxPatch
    n = len(steps)
    ax = ax or plt.subplots(figsize=(1.9 * n + 0.4, 2.3 if loop else 1.5))[1]
    w, h, gap = 1.5, 0.9, 0.45
    for i, (head, sub, col) in enumerate(steps):
        x = i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 0), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=_colour(col), ec="none"))
        ax.text(x + w / 2, h * 0.62, head, ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        ax.text(x + w / 2, h * 0.27, sub, ha="center", va="center", color="white", fontsize=8)
        if i < n - 1:
            ax.annotate("", xy=(x + w + gap - 0.03, h / 2), xytext=(x + w + 0.03, h / 2),
                        arrowprops=dict(arrowstyle="-|>", color="#525252", lw=1.5))
    if loop:
        a, b, text = loop
        xa, xb = a * (w + gap) + w / 2, b * (w + gap) + w / 2
        ax.annotate("", xy=(xb, -0.05), xytext=(xa, -0.05),
                    arrowprops=dict(arrowstyle="-|>", color="#525252", lw=1.5, connectionstyle="arc3,rad=-0.35", ls="--"))
        ax.text((xa + xb) / 2, -0.62, text, ha="center", va="center", fontsize=8.5, color="#525252")
    ax.set_xlim(-0.2, n * (w + gap) - gap + 0.2)
    ax.set_ylim(-0.9 if loop else -0.1, h + 0.25)
    ax.set_aspect("equal")
    ax.set_axis_off()
    if title:
        ax.set_title(title, fontsize=10)
    return ax


def plot_landscape(f, x_range, y_range, n=41, xlabel="", ylabel="", title="", marks=(), cmap="viridis", ax=None):
    """Heat map of f(x, y) on a grid (a "landscape"); marks = [(x, y, label, colour)] are drawn on top.

    Dark is low and bright is high (viridis); pass cmap="viridis_r" to turn that round.

    Example: plot_landscape(lambda b, g: energy([b, g]), (0, np.pi), (0, np.pi), xlabel="beta", ylabel="gamma").
    """
    ax = ax or plt.subplots(figsize=(4.6, 3.6))[1]
    xs, ys = np.linspace(*x_range, n), np.linspace(*y_range, n)
    z = np.array([[f(x, y) for x in xs] for y in ys])
    im = ax.imshow(z, origin="lower", extent=[x_range[0], x_range[1], y_range[0], y_range[1]], aspect="auto", cmap=cmap)
    plt.colorbar(im, ax=ax, shrink=0.85)
    for x, y, label, col in marks:
        ax.plot([x], [y], marker="*" if "best" in label or "end" in label else "o", ms=13, mfc=_colour(col), mec="white", ls="none", label=label)
    if marks:
        ax.legend(fontsize=8, loc="upper right")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    return ax


def plot_cost_histogram(diag, dists, title="", ax=None):
    """Grouped bars: for each cost value c, the total probability of landing on a choice with cost c, one bar per distribution.

    diag: cost of every basis state. dists: {label: probability array}. The first one is drawn grey (usually "random guessing").
    Example: plot_cost_histogram(diag, {"guessing": np.full(64, 1/64), "p = 3": probs3}).
    """
    ax = ax or plt.subplots(figsize=(6.5, 3.2))[1]
    diag = np.asarray(diag, dtype=float)
    levels = np.unique(np.round(diag, 9))
    width = 0.8 / len(dists)
    for k, (label, probs) in enumerate(dists.items()):
        probs = np.asarray(probs, dtype=float)
        vals = [probs[np.isclose(diag, c)].sum() for c in levels]
        ax.bar(np.arange(len(levels)) + (k - (len(dists) - 1) / 2) * width, vals, width, label=label, color=GREYS[min(k, len(GREYS) - 1)])
    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([f"{c:g}" for c in levels])
    ax.set_xlabel("cost of the choice  (lower is better)")
    ax.set_ylabel("probability of landing there")
    ax.legend(fontsize=8)
    ax.set_title(title, fontsize=10)
    return ax


def plot_phases(diag, gamma, title="", ax=None):
    """Polar picture of a cost layer: every choice's amplitude is turned by the angle -gamma * cost.

    One arrow per distinct cost value, coloured by cost; the lowest, the most common and the highest cost are labelled
    "cost c, k choices". Choices with the same cost point the same way.  Example: plot_phases(diag, gamma=0.3).
    """
    if ax is None:
        ax = plt.subplots(figsize=(3.8, 3.8), subplot_kw={"projection": "polar"})[1]
    diag = np.asarray(diag, dtype=float)
    levels = np.unique(np.round(diag, 9))
    counts = [int(np.isclose(diag, c).sum()) for c in levels]
    labelled = {0, len(levels) - 1, int(np.argmax(counts))}
    cmap = plt.get_cmap("viridis")
    for i, c in enumerate(levels):
        ang = -gamma * c
        col = cmap(i / max(1, len(levels) - 1))
        ax.annotate("", xy=(ang, 1.0), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
        if i in labelled:
            word = "choice" if counts[i] == 1 else "choices"
            ax.text(ang, 1.25, f"cost {c:g}\n{counts[i]} {word}", ha="center", va="center", fontsize=8)
    ax.set_ylim(0, 1.45)
    ax.set_yticks([])
    ax.set_title(title or f"phase of each choice, gamma = {gamma:g}", fontsize=9, pad=14)
    return ax


def plot_amplitude_stages(stages, suptitle="", ancilla_bit=0, highlight=None, labels=("helper = 0", "helper = 1")):
    """One bar chart per stage of a circuit: the (real) amplitude of every basis state, side by side.

    stages: dict {title: amplitude array}. By default positions whose bit number `ancilla_bit` is 1 are drawn magenta and the others
    teal (with the helper qubit as qubit 0 the odd positions stand out). With `highlight=[positions]` those positions are magenta
    instead (for example the marked states of a Grover search); `labels` names the (teal, magenta) groups in the legend. Returns the axes.
    Example: plot_amplitude_stages({"start": a0, "oracle": a1}, highlight=[3, 5], labels=("not marked", "marked")).
    """
    from matplotlib.patches import Patch
    n = len(stages)
    fig, axes = plt.subplots(1, n, figsize=(2.9 * n, 2.7), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, (name, amp) in zip(axes, stages.items()):
        amp = np.real(np.asarray(amp))
        k = np.arange(len(amp))
        if highlight is None:
            hot = ((k >> ancilla_bit) & 1).astype(bool)
        else:
            hot = np.isin(k, list(highlight))
        ax.bar(k, amp, color=[STOP_COLORS["use"] if h else STOP_COLORS["source"] for h in hot])
        ax.axhline(0, color="k", lw=0.6)
        ax.set_title(name, fontsize=10)
        if len(amp) <= 16:
            ax.set_xticks(k)
            ax.tick_params(axis="x", labelsize=7)
        ax.set_xlabel("position k")
    axes[0].set_ylabel("amplitude")
    axes[-1].legend(handles=[Patch(color=STOP_COLORS["source"], label=labels[0]), Patch(color=STOP_COLORS["use"], label=labels[1])],
                    fontsize=8, loc="best")
    if suptitle:
        fig.suptitle(suptitle, fontsize=10)
    fig.tight_layout()
    return axes


def plot_grover_geometry(theta, steps=3, ax=None):
    """Grover's algorithm as a rotation: the state starts at angle `theta` from the "not marked" axis and each step turns it by 2*theta.

    Horizontal axis = the "not marked" direction, vertical axis = the "marked" direction. The height of the arrow tip squared is the
    probability of a marked state: P = sin^2((2k + 1) * theta).  Example: plot_grover_geometry(np.arcsin(0.5), steps=2).
    """
    ax = ax or plt.subplots(figsize=(3.8, 3.8))[1]
    t = np.linspace(0, np.pi / 2, 100)
    ax.plot(np.cos(t), np.sin(t), color="#C6C6C6", lw=1)
    colours = [STOP_COLORS["source"], STOP_COLORS["move"], STOP_COLORS["store"], STOP_COLORS["use"], "#525252"]
    for k in range(steps + 1):
        ang = (2 * k + 1) * theta
        x, y = np.cos(ang), np.sin(ang)
        ax.annotate("", xy=(x, y), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=colours[k % len(colours)], lw=2))
        radius = 1.12 + 0.09 * (k % 2)                      # stagger the labels so neighbouring arrows do not collide
        ax.text(radius * x, radius * y, f"k={k}, P={np.sin(ang) ** 2:.2f}", ha="center", va="center", fontsize=8)
    ax.axhline(0, color="k", lw=0.6)
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)
    ax.set_aspect("equal")
    ax.set_xlabel("not marked")
    ax.set_ylabel("marked")
    ax.set_title("each Grover step turns the state by 2 x theta", fontsize=9)
    return ax
