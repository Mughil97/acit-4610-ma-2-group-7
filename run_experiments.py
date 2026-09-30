"""Entry point: run the MOEAs on every instance, config and seed, save the final fronts to results/fronts.csv,
and plot the first run of each combination to results/plots/ (shown on screen when there are 3 or fewer).

Examples:
    python run_experiments.py                                                    # everything, 10 runs each
    python run_experiments.py --algorithms vega --instances cap121 --configs C1 --runs 1
    python run_experiments.py --instances cap121 --configs C3 --runs 1 --watch   # watch one run live

Metrics (hypervolume) and statistical tests will be added here once app/utils has them.
"""

import argparse
import csv
import time

import matplotlib.pyplot as plt

from app.algorithms import available_algorithms, create_algorithm
from app.config import BASE_SEED, CONFIGS, INSTANCES, N_RUNS, RESULTS_DIR
from app.problem.loader import load_by_name
from app.utils.pareto import non_dominated
from app.utils.plotting import LivePlot, plot_run

ALL_INSTANCES = [name for names in INSTANCES.values() for name in names]
ALL_CONFIGS = [config.name for config in CONFIGS]
MAX_WINDOWS = 3  # more plots than this are only saved, not opened
PRINT_EVERY = 20  # with --watch, one terminal line every 20 generations
PROGRESS_HEADER = f"{'generation':>10}  {'cheapest f1':>12}  {'cheapest f2':>12}  {'trade-offs':>10}  {'opening costs':>13}"


def progress_line(number, objectives):
    """One terminal line about one generation."""
    cheapest_f1 = min(f1 for f1, _ in objectives)
    cheapest_f2 = min(f2 for _, f2 in objectives)
    opening_costs = len({f1 for f1, _ in objectives})
    return (f"{number:>10}  {cheapest_f1:>12,.0f}  {cheapest_f2:>12,.0f}  "
            f"{len(non_dominated(objectives)):>10}  {opening_costs:>13}")


def watch_live(moea, title):
    """Open a live window and print a terminal line every PRINT_EVERY generations while moea runs."""
    live = LivePlot(title)
    print(f"\n{title}\n{PROGRESS_HEADER}")

    def on_generation(number, objectives):
        live.update(number, objectives)
        if number % PRINT_EVERY == 0:
            print(progress_line(number, objectives), flush=True)

    moea.on_generation = on_generation
    return live


def run_once(algorithm, instance, config, seed, rows, watch=False):
    """Run once, print one line and add the front to rows; return the run's history, or None if it can not run."""
    start = time.perf_counter()
    moea = create_algorithm(algorithm, instance, config, seed)
    live = watch_live(moea, f"{algorithm.upper()} on {instance.name}, {config.name} (seed {seed})") if watch else None
    try:
        front = moea.run()
    except NotImplementedError:
        print(f"{algorithm} {instance.name}: skipped, {algorithm} is not implemented yet")
        if live:
            live.close()
        return None
    except ValueError as error:  # e.g. cap41/cap42 can not be solved
        print(f"{algorithm}: skipped, {error}")
        if live:
            live.close()
        return None
    seconds = time.perf_counter() - start

    if live and (len(moea.history) - 1) % PRINT_EVERY != 0:
        print(progress_line(len(moea.history) - 1, moea.history[-1]))  # the last generation
    print(f"{algorithm:<6} {instance.name:<7} {config.name}  seed {seed}:  {len(front)} trade-offs,"
          f"  best f1 {front[0][0]:>9,.0f},  best f2 {front[-1][1]:>12,.0f},  {seconds:.2f} s")
    for f1, f2 in front:
        rows.append([algorithm, instance.name, config.name, seed, round(seconds, 3), f1, f2])
    if live:
        live.keep_open()  # the window stays until you close it, then the next run starts
    return moea.history


def run_instance(algorithm, instance, configs, runs, rows, histories, watch):
    """Every config and seed of one algorithm on one instance; stops at the first run that can not run."""
    for config in configs:
        for run in range(runs):
            seed = BASE_SEED + run  # run 1 uses seed 42, run 2 uses seed 43, ...
            history = run_once(algorithm, instance, config, seed, rows, watch=watch and run == 0)
            if history is None:
                return
            if run == 0:
                histories[(algorithm, instance.name, config.name)] = history


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--algorithms", nargs="+", choices=available_algorithms(), default=["vega"],
                        help="algorithms to run (default: vega, the only one implemented)")
    parser.add_argument("--instances", nargs="+", choices=ALL_INSTANCES, default=ALL_INSTANCES,
                        help="instance names, e.g. cap101 cap121 (default: all six)")
    parser.add_argument("--configs", nargs="+", choices=ALL_CONFIGS, default=ALL_CONFIGS,
                        help="config names, e.g. C1 C2 C3 (default: all three)")
    parser.add_argument("--runs", type=int, default=N_RUNS,
                        help=f"independent runs (seeds) per combination (default: {N_RUNS})")
    parser.add_argument("--watch", action="store_true",
                        help="watch the first run of each combination live: a window updated every generation "
                             f"and a terminal line every {PRINT_EVERY} generations")
    args = parser.parse_args()

    configs = [config for config in CONFIGS if config.name in args.configs]
    rows = []  # one row per point of every final front
    histories = {}  # {(algorithm, instance, config): history of the first run}

    for algorithm in args.algorithms:
        for instance_name in args.instances:
            run_instance(algorithm, load_by_name(instance_name), configs, args.runs, rows, histories, args.watch)

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / "fronts.csv"
    with open(out_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "instance", "config", "seed", "seconds", "f1", "f2"])
        writer.writerows(rows)
    print(f"\nsaved {len(rows)} front points to {out_path}")

    plots_dir = RESULTS_DIR / "plots"
    plots_dir.mkdir(exist_ok=True)
    for (algorithm, instance_name, config_name), history in histories.items():
        title = f"{algorithm.upper()} on {instance_name}, {config_name} (seed {BASE_SEED})"
        figure = plot_run(history, title, plots_dir / f"{algorithm}_{instance_name}_{config_name}.png")
        if args.watch or len(histories) > MAX_WINDOWS:
            plt.close(figure)
    plural = "s" if len(histories) != 1 else ""
    print(f"saved {len(histories)} plot{plural} (the first run of each combination) to {plots_dir}")

    if not args.watch and 0 < len(histories) <= MAX_WINDOWS:
        plt.show()  # pop the plots open, like the lab


if __name__ == "__main__":
    main()
