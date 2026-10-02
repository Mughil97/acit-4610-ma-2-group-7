"""Plots of algorithm runs."""

import time

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator

from app.utils.pareto import non_dominated

WITH_COMMAS = FuncFormatter(lambda value, _: f"{value:,.0f}")
F1_LABEL = "f1: opening cost"
F2_LABEL = "f2: allocation cost"
FRAME_STEP = 4  # the window shows every 4th generation (and the last one), so a run plays in a few seconds
SECONDS_BEFORE_CLOSING = 2  # with several combinations: how long the last generation stays on screen


def plot_fronts(fronts, title, out_path):
    """Every algorithm's final front on the same axes ({name: list of (f1, f2)}); saved to out_path."""
    fig, ax = plt.subplots(figsize=(8, 6))
    for name, front in fronts.items():
        ax.plot([f1 for f1, _ in front], [f2 for _, f2 in front], "o-", label=f"{name} ({len(front)} trade-offs)")
    ax.set(title=title, xlabel=F1_LABEL, ylabel=F2_LABEL)
    ax.xaxis.set_major_formatter(WITH_COMMAS)
    ax.yaxis.set_major_formatter(WITH_COMMAS)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    return fig


def plot_run(history, title, out_path):
    """One run in three pictures: start vs end, best cost per generation, variety left. Saved to out_path."""
    first, last = history[0], history[-1]
    front = non_dominated(last)
    generations = range(len(history))
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(17, 5))

    # 1. where the population started (grey) and ended (blue), and the final trade-offs (red)
    ax1.scatter([f1 for f1, _ in first], [f2 for _, f2 in first], color="lightgray", label="start: random population")
    ax1.plot([f1 for f1, _ in front], [f2 for _, f2 in front], "o-", color="red", markerfacecolor="none",
             markersize=10, zorder=2, label=f"final trade-offs ({len(front)})")  # rings under the dots
    ax1.scatter([f1 for f1, _ in last], [f2 for _, f2 in last], alpha=0.6, zorder=3,
                label=f"end: last generation ({len(last)})")
    ax1.set(title="Where the population started and ended", xlabel=F1_LABEL, ylabel=F2_LABEL)
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


def zoom_to(ax, points):
    """Fit the axes around these (f1, f2) points, with a small margin."""
    f1s, f2s = [f1 for f1, _ in points], [f2 for _, f2 in points]
    f1_margin = 0.08 * (max(f1s) - min(f1s)) or 0.05 * max(f1s) or 1
    f2_margin = 0.08 * (max(f2s) - min(f2s)) or 0.05 * max(f2s) or 1
    ax.set_xlim(min(f1s) - f1_margin, max(f1s) + f1_margin)
    ax.set_ylim(min(f2s) - f2_margin, max(f2s) + f2_margin)


def animate_runs(histories, title, on_frame=None, close_when_done=False, milliseconds_per_frame=120):
    """Play runs side by side ({name: history}), one generation per frame; on_frame(number) runs with every frame."""
    last = max(len(history) for history in histories.values()) - 1
    fig, axes = plt.subplots(1, len(histories), figsize=(7 * len(histories), 6), squeeze=False)

    panels = {}  # name -> (axes, trade-off line, population dots)
    for ax, name in zip(axes[0], histories):
        ax.set(xlabel=F1_LABEL, ylabel=F2_LABEL)
        ax.xaxis.set_major_formatter(WITH_COMMAS)
        ax.yaxis.set_major_formatter(WITH_COMMAS)
        ax.grid(alpha=0.25)
        # trade-offs as hollow rings drawn under the dots, so no part of the population is hidden
        (line,) = ax.plot([], [], "o-", color="red", markerfacecolor="none", markersize=10, zorder=2,
                          label="trade-offs")
        dots = ax.scatter([], [], alpha=0.6, zorder=3, label="population")
        ax.legend(loc="upper right")
        panels[name] = (ax, line, dots)

    def draw(number):
        for name, (ax, line, dots) in panels.items():
            generation = histories[name][min(number, len(histories[name]) - 1)]
            front = non_dominated(generation)
            dots.set_offsets(generation)
            line.set_data([f1 for f1, _ in front], [f2 for _, f2 in front])
            zoom_to(ax, generation)  # each panel follows its own population
            ax.set_title(f"{name}: {len(generation)} solutions, {len(front)} trade-offs")
        fig.suptitle(f"{title}, generation {number} of {last} (each panel has its own scale)")

    def window_open():
        return plt.fignum_exists(fig.number)  # False once the window has been closed

    def wait(seconds):
        """Keep the window responsive for this many seconds; stops early if it is closed."""
        end = time.perf_counter() + seconds
        while window_open() and end - time.perf_counter() > 0.001:
            fig.canvas.start_event_loop(min(end - time.perf_counter(), 0.05))  # never 0: that means "forever"

    # A plain loop plays the frames and closes the window, so nothing ever waits for a GUI timer or event
    # (on macOS, closing a window from inside plt.show() can wait for the next mouse or keyboard event).
    plt.show(block=False)
    for number in list(range(0, last, FRAME_STEP)) + [last]:
        if not window_open():
            break  # closed by hand: stop playing, the experiment goes on
        frame_started = time.perf_counter()
        draw(number)
        fig.canvas.draw()
        fig.canvas.flush_events()  # put the frame on screen now (on macOS, draw() only marks the window as changed)
        if on_frame:
            on_frame(number)
        time_left = milliseconds_per_frame / 1000 - (time.perf_counter() - frame_started)
        wait(max(time_left, 0.01))  # always a short pause, so the window keeps responding

    if close_when_done:
        wait(SECONDS_BEFORE_CLOSING)
        plt.close(fig)
    elif window_open():
        plt.show()  # a single combination: the window stays until it is closed by hand
    return fig
