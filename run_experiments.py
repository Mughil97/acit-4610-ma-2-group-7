"""Entry point: run the MOEAs on every instance, config and seed, play the first run of each in a window,
save the fronts and pictures to results/, and print a hypervolume table (saved to results/summary.csv).

Examples:
    python run_experiments.py                                                    # everything, 10 runs each
    python run_experiments.py --instances cap121 --configs C3 --runs 1           # one run of each algorithm

Statistical tests will be added here later.
"""

import argparse
import csv
import time
from statistics import mean, stdev

import matplotlib.pyplot as plt

from app.algorithms import available_algorithms, create_algorithm
from app.config import BASE_SEED, CONFIGS, INSTANCES, N_RUNS, RESULTS_DIR
from app.problem.loader import load_by_name
from app.utils.metrics import REFERENCE_POINT, hypervolume_2d, normalise
from app.utils.pareto import non_dominated
from app.utils.plotting import animate_run, plot_fronts, plot_run

ALL_INSTANCES = [name for names in INSTANCES.values() for name in names]
ALL_CONFIGS = [config.name for config in CONFIGS]
PRINT_EVERY = 20  # one terminal line every 20 generations while a run plays
PROGRESS_HEADER = f"{'generation':>10}  {'cheapest f1':>12}  {'cheapest f2':>12}  {'trade-offs':>10}  {'opening costs':>13}"


def progress_line(number, objectives):
    """One terminal line about one generation."""
    cheapest_f1 = min(f1 for f1, _ in objectives)
    cheapest_f2 = min(f2 for _, f2 in objectives)
    opening_costs = len({f1 for f1, _ in objectives})
    return (f"{number:>10}  {cheapest_f1:>12,.0f}  {cheapest_f2:>12,.0f}  "
            f"{len(non_dominated(objectives)):>10}  {opening_costs:>13}")


def watch_run(history, title, close_when_done):
    """Play the run in a window, with a terminal line every PRINT_EVERY generations in step with it."""
    last = len(history) - 1
    print(f"\n{title}\n{PROGRESS_HEADER}")

    def on_frame(number, objectives):
        if number % PRINT_EVERY == 0 or number == last:
            print(progress_line(number, objectives), flush=True)

    animate_run(history, title, on_frame, close_when_done)  # returns when the window is closed


def run_once(algorithm, instance, config, seed, rows, watch, close_window):
    """Run once, print one line and add the front to rows; return (name, history), or None if it can not run."""
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
    if watch:
        watch_run(moea.history, f"{moea.name} on {instance.name}, {config.name} (seed {seed})", close_window)
    return moea.name, moea.history


def run_combination(algorithm, instance, config, runs, rows, close_window):
    """Every seed of one algorithm on one instance and config; return (name, history) of the first run, or None."""
    first = None
    for run in range(runs):
        seed = BASE_SEED + run  # run 1 uses seed 42, run 2 uses seed 43, ...
        result = run_once(algorithm, instance, config, seed, rows, run == 0, close_window)  # play the first run
        if result is None:
            return None
        if run == 0:
            first = result
    return first


def save_checkpoint(rows, instance_name, config_name, first_runs):
    """Save a picture of each algorithm's first run, both fronts together, and every front point so far."""
    plots_dir = RESULTS_DIR / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    fronts = {}
    for algorithm, (name, history) in first_runs.items():
        title = f"{name} on {instance_name}, {config_name} (seed {BASE_SEED})"
        plt.close(plot_run(history, title, plots_dir / f"{algorithm}_{instance_name}_{config_name}.png"))
        fronts[name] = non_dominated(history[-1])
    title = f"Final fronts on {instance_name}, {config_name} (seed {BASE_SEED})"
    plt.close(plot_fronts(fronts, title, plots_dir / f"compare_{instance_name}_{config_name}.png"))

    with open(RESULTS_DIR / "fronts.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "instance", "config", "seed", "seconds", "f1", "f2"])
        writer.writerows(rows)

    print(f"checkpoint: saved {len(first_runs) + 1} pictures to results/plots/ "
          f"and {len(rows)} front points so far to results/fronts.csv", flush=True)


def summarise(rows):
    """Hypervolume of every run, scaled the same way for every algorithm on an instance; print and save a table."""
    runs = {}  # (algorithm, instance, config, seed) -> its front and run time
    scale = {}  # instance -> (ideal, nadir): the best and worst f1 and f2 that any run found on it
    for algorithm, instance, config, seed, seconds, f1, f2 in rows:
        runs.setdefault((algorithm, instance, config, seed), {"front": [], "seconds": seconds})["front"].append((f1, f2))
        low, high = scale.get(instance, ((f1, f2), (f1, f2)))
        scale[instance] = ((min(low[0], f1), min(low[1], f2)), (max(high[0], f1), max(high[1], f2)))

    results = {}  # (algorithm, instance, config) -> [(hypervolume, trade-offs, seconds) of every run]
    for (algorithm, instance, config, _), run in runs.items():
        hv = hypervolume_2d(normalise(run["front"], *scale[instance]))
        results.setdefault((algorithm, instance, config), []).append((hv, len(run["front"]), run["seconds"]))

    table = []
    for (algorithm, instance, config), values in results.items():
        hvs = [hv for hv, _, _ in values]
        table.append([algorithm, instance, config, len(values), mean(hvs), stdev(hvs) if len(hvs) > 1 else 0.0,
                      max(hvs), min(hvs), mean(n for _, n, _ in values), mean(s for _, _, s in values)])

    print(f"\nHypervolume (HV): each instance scaled to 0..1 between the best and worst values any run found on it, "
          f"reference point {REFERENCE_POINT}; bigger is better.")
    print(f"{'algorithm':<10}{'instance':<9}{'config':<7}{'runs':>5}{'HV mean':>9}{'HV std':>8}{'HV best':>9}"
          f"{'HV worst':>9}{'trade-offs':>11}{'seconds':>9}")
    for algorithm, instance, config, n, hv_mean, hv_std, hv_best, hv_worst, trade_offs, seconds in table:
        print(f"{algorithm:<10}{instance:<9}{config:<7}{n:>5}{hv_mean:>9.3f}{hv_std:>8.3f}{hv_best:>9.3f}"
              f"{hv_worst:>9.3f}{trade_offs:>11.1f}{seconds:>9.2f}")

    with open(RESULTS_DIR / "summary.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "instance", "config", "runs", "hv_mean", "hv_std", "hv_best", "hv_worst",
                         "mean_trade_offs", "mean_seconds"])
        writer.writerows(table)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--algorithms", nargs="+", choices=available_algorithms(), default=["vega", "nsga2"],
                        help="algorithms to run (default: both)")
    parser.add_argument("--instances", nargs="+", choices=ALL_INSTANCES, default=ALL_INSTANCES,
                        help="instance names, e.g. cap101 cap121 (default: all six)")
    parser.add_argument("--configs", nargs="+", choices=ALL_CONFIGS, default=ALL_CONFIGS,
                        help="config names, e.g. C1 C2 C3 (default: all three)")
    parser.add_argument("--runs", type=int, default=N_RUNS,
                        help=f"independent runs (seeds) per combination (default: {N_RUNS})")
    args = parser.parse_args()

    configs = [config for config in CONFIGS if config.name in args.configs]
    rows = []  # one row per point of every final front
    # several combinations: each window closes by itself, so the next one can start
    close_windows = len(args.algorithms) * len(args.instances) * len(configs) > 1

    for instance_name in args.instances:
        instance = load_by_name(instance_name)
        print(f"\nloading {instance_name}: {instance.m} facilities, {instance.n} customers", flush=True)
        for config in configs:
            print(f"{instance.name}, {config.name}: {args.runs} runs of {' and '.join(args.algorithms)} "
                  f"(population {config.pop_size}, {config.max_evaluations:,} evaluations each)", flush=True)
            first_runs = {}
            for algorithm in args.algorithms:
                first = run_combination(algorithm, instance, config, args.runs, rows, close_windows)
                if first:
                    first_runs[algorithm] = first
            if first_runs:
                save_checkpoint(rows, instance.name, config.name, first_runs)

    if rows:
        summarise(rows)
    print("\ndone: results/fronts.csv, results/summary.csv and pictures in results/plots/")


if __name__ == "__main__":
    main()
