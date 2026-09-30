"""Entry point: run the MOEAs on every instance, config and seed, save the final fronts to results/fronts.csv,
and plot the first run of each combination to results/plots/ (shown on screen when there are 3 or fewer).

Examples:
    python run_experiments.py                                                    # everything, 10 runs each
    python run_experiments.py --algorithms vega --instances cap121 --configs C1 --runs 1

Metrics (hypervolume) and statistical tests will be added here once app/utils has them.
"""

import argparse
import csv
import time

import matplotlib.pyplot as plt

from app.algorithms import available_algorithms, create_algorithm
from app.config import BASE_SEED, CONFIGS, INSTANCES, N_RUNS, RESULTS_DIR
from app.problem.loader import load_by_name
from app.utils.plotting import plot_run

ALL_INSTANCES = [name for names in INSTANCES.values() for name in names]
ALL_CONFIGS = [config.name for config in CONFIGS]
MAX_WINDOWS = 3  # more plots than this are only saved, not opened


def run_once(algorithm, instance, config, seed, rows):
    """Run once, print one line and add the front to rows; return the run's history, or None if it can not run."""
    start = time.perf_counter()
    moea = create_algorithm(algorithm, instance, config, seed)
    try:
        front = moea.run()
    except NotImplementedError:
        print(f"{algorithm} {instance.name}: skipped, {algorithm} is not implemented yet")
        return None
    except ValueError as error:  # e.g. cap41/cap42 can not be solved
        print(f"{algorithm}: skipped, {error}")
        return None
    seconds = time.perf_counter() - start

    print(f"{algorithm:<6} {instance.name:<7} {config.name}  seed {seed}:  {len(front)} trade-offs,"
          f"  best f1 {front[0][0]:>9,.0f},  best f2 {front[-1][1]:>12,.0f},  {seconds:.2f} s")
    for f1, f2 in front:
        rows.append([algorithm, instance.name, config.name, seed, round(seconds, 3), f1, f2])
    return moea.history


def run_instance(algorithm, instance, configs, runs, rows, histories):
    """Every config and seed of one algorithm on one instance; stops at the first run that can not run."""
    for config in configs:
        for run in range(runs):
            history = run_once(algorithm, instance, config, BASE_SEED + run, rows)  # run 1 uses seed 42, ...
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
    args = parser.parse_args()

    configs = [config for config in CONFIGS if config.name in args.configs]
    rows = []  # one row per point of every final front
    histories = {}  # {(algorithm, instance, config): history of the first run}

    for algorithm in args.algorithms:
        for instance_name in args.instances:
            run_instance(algorithm, load_by_name(instance_name), configs, args.runs, rows, histories)

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
        if len(histories) > MAX_WINDOWS:
            plt.close(figure)
    plural = "s" if len(histories) != 1 else ""
    print(f"saved {len(histories)} plot{plural} (the first run of each combination) to {plots_dir}")

    if 0 < len(histories) <= MAX_WINDOWS:
        plt.show()  # pop the plots open, like the lab


if __name__ == "__main__":
    main()
