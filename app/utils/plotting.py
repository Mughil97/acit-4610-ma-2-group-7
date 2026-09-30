"""Plots of one algorithm run."""

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

from app.utils.pareto import non_dominated

WITH_COMMAS = FuncFormatter(lambda value, _: f"{value:,.0f}")


def plot_run(history, title, out_path):
    """One run in three pictures: start vs end, best cost per generation, variety left. Saved to out_path."""
    first, last = history[0], history[-1]
    front = non_dominated(last)
    generations = range(len(history))
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(17, 5))

    # 1. where the population started (grey) and ended (blue), and the final trade-offs (red)
    ax1.scatter([f1 for f1, _ in first], [f2 for _, f2 in first], color="lightgray", label="start: random population")
    ax1.scatter([f1 for f1, _ in last], [f2 for _, f2 in last], alpha=0.6, label="end: last generation")
    ax1.plot([f1 for f1, _ in front], [f2 for _, f2 in front], "o-", color="red",
             label=f"final trade-offs ({len(front)})")
    ax1.set(title="Where the population started and ended", xlabel="f1: opening cost", ylabel="f2: allocation cost")
    ax1.xaxis.set_major_locator(MaxNLocator(5))
    ax1.xaxis.set_major_formatter(WITH_COMMAS)
    ax1.yaxis.set_major_formatter(WITH_COMMAS)

    # 2. the cheapest f1 and f2 in every generation, as a percentage of the starting value
    best_f1 = [min(f1 for f1, _ in generation) for generation in history]
    best_f2 = [min(f2 for _, f2 in generation) for generation in history]
    ax2.plot(generations, [100 * v / (best_f1[0] or 1) for v in best_f1], label="cheapest f1 (opening)")
    ax2.plot(generations, [100 * v / (best_f2[0] or 1) for v in best_f2], label="cheapest f2 (allocation)")
    ax2.set(title="How the best costs changed", xlabel="generation", ylabel="% of the starting value")

    # 3. how many different opening costs (facility counts) and trade-offs are left in the population
    ax3.plot(generations, [len({f1 for f1, _ in generation}) for generation in history],
             label="different opening costs (f1)")
    ax3.plot(generations, [len(non_dominated(generation)) for generation in history], label="trade-offs")
    ax3.set(title="How much variety is left", xlabel="generation", ylabel="count")

    for ax in (ax1, ax2, ax3):
        ax.grid(alpha=0.25)
        ax.legend()
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    return fig
