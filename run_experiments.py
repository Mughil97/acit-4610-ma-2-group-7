"""Entry point: run the MOEAs on every instance, config and seed, play the first run of each combination in a
window, save the final fronts to results/fronts.csv and a picture of each first run to results/plots/.

Examples:
    python run_experiments.py                                                    # everything, 10 runs each
    python run_experiments.py --instances cap121 --configs C3 --runs 1           # one run

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
from app.utils.plotting import animate_run, plot_run

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


def save_checkpoint(rows, algorithm, instance_name, config_name, history):
    """Save the picture of this combination's first run and every front point so far; print what was saved."""
    plots_dir = RESULTS_DIR / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    picture = plots_dir / f"{algorithm}_{instance_name}_{config_name}.png"
    title = f"{algorithm.upper()} on {instance_name}, {config_name} (seed {BASE_SEED})"
    plt.close(plot_run(history, title, picture))

    fronts = RESULTS_DIR / "fronts.csv"
    with open(fronts, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "instance", "config", "seed", "seconds", "f1", "f2"])
        writer.writerows(rows)

    print(f"checkpoint: saved results/plots/{picture.name} and {len(rows)} front points so far to results/fronts.csv",
          flush=True)


def run_once(algorithm, instance, config, seed, rows, watch=False, close_window=False):
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
    if watch:
        title = f"{algorithm.upper()} on {instance.name}, {config.name} (seed {seed})"
        watch_run(moea.history, title, close_window)
    return moea.history


def run_instance(algorithm, instance, configs, runs, rows, close_windows):
    """Every config and seed of one algorithm on one instance, with a checkpoint after each config."""
    for config in configs:
        print(f"{instance.name}, {config.name}: {runs} runs "
              f"(population {config.pop_size}, {config.max_evaluations:,} evaluations each)", flush=True)
        first_history = None
        for run in range(runs):
            seed = BASE_SEED + run  # run 1 uses seed 42, run 2 uses seed 43, ...
            history = run_once(algorithm, instance, config, seed, rows, run == 0, close_windows)  # play the first
            if history is None:
                return
            if run == 0:
                first_history = history
        if first_history:
            save_checkpoint(rows, algorithm, instance.name, config.name, first_history)


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
    # several combinations: each window closes by itself, so the next one can start
    close_windows = len(args.algorithms) * len(args.instances) * len(configs) > 1

    for algorithm in args.algorithms:
        for instance_name in args.instances:
            instance = load_by_name(instance_name)
            print(f"\nloading {instance_name}: {instance.m} facilities, {instance.n} customers", flush=True)
            run_instance(algorithm, instance, configs, args.runs, rows, close_windows)

    print(f"done: {len(rows)} front points in results/fronts.csv, pictures in results/plots/")


if __name__ == "__main__":
    main()
