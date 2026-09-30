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


class LivePlot:
    """A window that opens when a run starts and shows the population after every generation."""

    def __init__(self, title):
        plt.ion()  # interactive mode: the window updates while the algorithm keeps running
        self.title = title
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.set(xlabel="f1: opening cost", ylabel="f2: allocation cost")
        self.ax.xaxis.set_major_formatter(WITH_COMMAS)
        self.ax.yaxis.set_major_formatter(WITH_COMMAS)
        self.ax.grid(alpha=0.25)
        self.dots = self.ax.scatter([], [], alpha=0.6, label="population")
        (self.line,) = self.ax.plot([], [], "o-", color="red", label="trade-offs")
        self.ax.legend(loc="upper right")
        self.lowest = self.highest = None  # smallest and largest (f1, f2) seen so far

    def update(self, number, objectives):
        front = non_dominated(objectives)
        self.dots.set_offsets(objectives)
        self.line.set_data([f1 for f1, _ in front], [f2 for _, f2 in front])

        # the axes only grow, so the start stays visible and the movement can be seen
        f1s, f2s = [f1 for f1, _ in objectives], [f2 for _, f2 in objectives]
        if self.lowest is None:
            self.lowest, self.highest = [min(f1s), min(f2s)], [max(f1s), max(f2s)]
        self.lowest = [min(self.lowest[0], min(f1s)), min(self.lowest[1], min(f2s))]
        self.highest = [max(self.highest[0], max(f1s)), max(self.highest[1], max(f2s))]
        self.ax.set_xlim(self.lowest[0] * 0.95, self.highest[0] * 1.05)
        self.ax.set_ylim(self.lowest[1] * 0.95, self.highest[1] * 1.05)

        self.ax.set_title(f"{self.title}\ngeneration {number}: {len(front)} trade-offs")
        plt.pause(0.01)  # draw now

    def keep_open(self):
        plt.ioff()
        plt.show()  # the last generation stays until the window is closed

    def close(self):
        plt.close(self.fig)
        plt.ioff()
