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
STYLES = {"VEGA": ("o-", "tab:blue", 3), "NSGA-II": ("s-", "tab:orange", 2)}  # VEGA's circles drawn on top


def draw_fronts(ax, fronts, title, populations=None):
    """Each algorithm's trade-offs, and its population if given, on one plot with one shared scale ({name: points})."""
    ax.clear()
    for name, front in fronts.items():
        line_style, color, layer = STYLES.get(name, ("^-", None, 1))
        ax.plot([f1 for f1, _ in front], [f2 for _, f2 in front], line_style, color=color, zorder=layer,
                markersize=9, markerfacecolor="white", markeredgewidth=1.6, linewidth=1.8,
                label=f"{name} trade-offs ({len(front)})")  # big hollow rings
        if populations:  # small dots on top: a dot inside a ring is a population member on the front
            population = populations[name]
            ax.scatter([f1 for f1, _ in population], [f2 for _, f2 in population], s=9, color=color, alpha=0.75,
                       linewidths=0, zorder=4, label=f"{name} population ({len(population)})")
    ax.set(title=f"{' vs '.join(fronts)} - {title}", xlabel=F1_LABEL, ylabel=F2_LABEL)
    ax.xaxis.set_major_formatter(WITH_COMMAS)
    ax.yaxis.set_major_formatter(WITH_COMMAS)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")


def plot_fronts(fronts, title, out_path):
    """Every algorithm's final front on one plot ({name: list of (f1, f2)}); saved to out_path."""
    fig, ax = plt.subplots(figsize=(8, 6))
    draw_fronts(ax, fronts, title)
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


def animate_runs(histories, title, on_frame=None, close_when_done=False, milliseconds_per_frame=120):
    """Play runs ({name: history}) on one plot, one generation per frame; on_frame(number) runs with every frame."""
    last = max(len(history) for history in histories.values()) - 1
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.canvas.manager.set_window_title(f"{' vs '.join(histories)} - {title}")
    fig.subplots_adjust(left=0.15, right=0.96, top=0.93, bottom=0.1)  # fixed margins, so the plot does not jump

    def draw(number):
        generations = {name: history[min(number, len(history) - 1)] for name, history in histories.items()}
        fronts = {name: non_dominated(generation) for name, generation in generations.items()}
        draw_fronts(ax, fronts, f"{title}, generation {number} of {last}", generations)

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
