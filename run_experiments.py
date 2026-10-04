"""Entry point: run VEGA and NSGA-II at the same time on every instance, config and seed, play their first runs
together on one plot, save fronts and pictures to results/, and print a hypervolume table (results/summary.csv).

Examples:
    python run_experiments.py                                                    # everything, 10 runs each
    python run_experiments.py --instances cap121 --configs C3 --runs 1           # one run of each algorithm
    python run_experiments.py --representation integer                           # saved in results/integer/

The runner also writes per-run metrics and paired Wilcoxon HV comparisons.
"""

import argparse
import csv
import time
from concurrent.futures import ProcessPoolExecutor
from statistics import mean, stdev

import matplotlib
matplotlib.use("Agg")  # headless backend: safe with ProcessPoolExecutor on Windows
import matplotlib.pyplot as plt

from app.algorithms import available_algorithms, create_algorithm
from app.config import BASE_SEED, CONFIGS, INSTANCES, N_RUNS, RESULTS_DIR
from app.problem.loader import load_by_name
from app.utils.metrics import REFERENCE_POINT, hypervolume_2d, normalise
from app.utils.pareto import non_dominated
from app.utils.plotting import plot_fronts, plot_run
from app.utils.statistics import paired_wilcoxon

ALL_INSTANCES = [name for names in INSTANCES.values() for name in names]
ALL_CONFIGS = [config.name for config in CONFIGS]
PRINT_EVERY = 20  # one terminal line every 20 generations while the runs play


def run_seed(algorithm, instance_name, config_name, seed, keep_history, representation):
    """One run, done in its own process; return (name, front, seconds, history or None)."""
    config = next(config for config in CONFIGS if config.name == config_name)
    start = time.perf_counter()
    moea = create_algorithm(algorithm, load_by_name(instance_name), config, seed, representation)
    front = moea.run()
    return moea.name, front, time.perf_counter() - start, moea.history if keep_history else None


def progress_header(histories):
    names = "".join(f"  {name:<34}" for name in histories)
    columns = "".join(f"  {'cheapest f1':>11} {'cheapest f2':>11} {'trade-offs':>10}" for _ in histories)
    return f"{'':>10}{names}\n{'generation':>10}{columns}"


def progress_line(number, histories):
    """One terminal line about one generation of every run, next to each other."""
    line = f"{number:>10}"
    for history in histories.values():
        generation = history[min(number, len(history) - 1)]
        cheapest_f1 = min(f1 for f1, _ in generation)
        cheapest_f2 = min(f2 for _, f2 in generation)
        line += f"  {cheapest_f1:>11,.0f} {cheapest_f2:>11,.0f} {len(non_dominated(generation)):>10}"
    return line


def watch_runs(histories, title, close_when_done):
    """Print synchronized progress for the first runs without opening GUI windows.

    Final figures are still saved to results/plots/. Avoiding a Tk GUI here makes the
    ProcessPoolExecutor run reliable on Windows and does not change either MOEA.
    """
    last = max(len(history) for history in histories.values()) - 1
    print(f"\n{title}\n{progress_header(histories)}")
    numbers = list(range(0, last + 1, PRINT_EVERY))
    if not numbers or numbers[-1] != last:
        numbers.append(last)
    for number in numbers:
        print(progress_line(number, histories), flush=True)


def run_combination(pool, instance_name, config, algorithms, runs, rows, close_window, representation):
    """Start every algorithm and seed at the same time, play the first runs together, then collect the rest."""
    futures = {(algorithm, run): pool.submit(run_seed, algorithm, instance_name, config.name, BASE_SEED + run,
                                             run == 0, representation)
               for algorithm in algorithms for run in range(runs)}

    first_runs, failed = {}, set()  # first_runs: algorithm -> (name, history of seed 42)
    for algorithm in algorithms:
        try:
            name, _, _, history = futures[(algorithm, 0)].result()
            first_runs[algorithm] = (name, history)
        except (NotImplementedError, ValueError) as error:  # e.g. cap41/cap42 can not be solved
            print(f"{algorithm} {instance_name}: skipped, {str(error) or 'not implemented yet'}")
            failed.add(algorithm)

    if first_runs:  # the other seeds keep running in the background while the window plays
        title = f"{instance_name} - {config.name} (seed {BASE_SEED})"
        watch_runs(dict(first_runs.values()), title, close_window)

    for (algorithm, run), future in futures.items():
        if algorithm not in failed:
            _, front, seconds, _ = future.result()
            seed = BASE_SEED + run
            print(f"{algorithm:<5} {instance_name:<6} {config.name} seed {seed}: {len(front)} trade-offs, "
                  f"best f1 {front[0][0]:,.0f}, best f2 {front[-1][1]:,.0f}, {seconds:.2f} s", flush=True)
            for f1, f2 in front:
                rows.append([algorithm, instance_name, config.name, seed, round(seconds, 3), f1, f2])
    return first_runs


def save_pictures(instance_name, config_name, first_runs, results_dir):
    """A picture of each algorithm's first run, and both together like the live window's last frame."""
    plots_dir = results_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    fronts, populations = {}, {}
    for algorithm, (name, history) in first_runs.items():
        title = f"{name} - {instance_name} - {config_name} (seed {BASE_SEED})"
        plt.close(plot_run(history, title, plots_dir / f"{algorithm}_{instance_name}_{config_name}.png"))
        fronts[name], populations[name] = non_dominated(history[-1]), history[-1]
    last = max(len(history) for _, history in first_runs.values()) - 1
    title = f"{instance_name} - {config_name} (seed {BASE_SEED}), generation {last} of {last}"
    plt.close(plot_fronts(fronts, title, plots_dir / f"compare_{instance_name}_{config_name}.png", populations))


def save_checkpoint(rows, instance_name, config_name, first_runs, results_dir):
    """Save the pictures of the first runs, and every front point so far."""
    save_pictures(instance_name, config_name, first_runs, results_dir)

    with open(results_dir / "fronts.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "instance", "config", "seed", "seconds", "f1", "f2"])
        writer.writerows(rows)

    folder = results_dir.relative_to(RESULTS_DIR.parent)
    print(f"checkpoint: saved {len(first_runs) + 1} pictures to {folder}/plots/ "
          f"and {len(rows)} front points so far to {folder}/fronts.csv", flush=True)


def summarise(rows, results_dir):
    """Save per-run metrics, aggregate summaries, and paired HV statistical comparisons."""
    runs = {}  # (algorithm, instance, config, seed) -> its front and run time
    scale = {}  # instance -> (ideal, nadir): shared empirical scaling across all included runs/configs/algorithms
    for algorithm, instance, config, seed, seconds, f1, f2 in rows:
        runs.setdefault((algorithm, instance, config, seed), {"front": [], "seconds": seconds})["front"].append((f1, f2))
        low, high = scale.get(instance, ((f1, f2), (f1, f2)))
        scale[instance] = ((min(low[0], f1), min(low[1], f2)), (max(high[0], f1), max(high[1], f2)))

    per_run = []
    grouped = {}
    for (algorithm, instance, config, seed), run in sorted(runs.items()):
        hv = hypervolume_2d(normalise(run["front"], *scale[instance]))
        record = [algorithm, instance, config, seed, hv, len(run["front"]), run["seconds"]]
        per_run.append(record)
        grouped.setdefault((algorithm, instance, config), []).append((seed, hv, len(run["front"]), run["seconds"]))

    with open(results_dir / "run_metrics.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "instance", "config", "seed", "hypervolume", "non_dominated", "seconds"])
        writer.writerows(per_run)

    table = []
    for (algorithm, instance, config), values in sorted(grouped.items()):
        hvs = [hv for _, hv, _, _ in values]
        table.append([algorithm, instance, config, len(values), mean(hvs), stdev(hvs) if len(hvs) > 1 else 0.0,
                      max(hvs), min(hvs), mean(n for _, _, n, _ in values), mean(sec for _, _, _, sec in values)])

    print(f"\nHypervolume (HV): each instance scaled to 0..1 between the best and worst values any included run found "
          f"on it, reference point {REFERENCE_POINT}; bigger is better.")
    print(f"{'algorithm':<10}{'instance':<9}{'config':<7}{'runs':>5}{'HV mean':>9}{'HV std':>8}{'HV best':>9}"
          f"{'HV worst':>9}{'trade-offs':>11}{'seconds':>9}")
    for algorithm, instance, config, n, hv_mean, hv_std, hv_best, hv_worst, trade_offs, seconds in table:
        print(f"{algorithm:<10}{instance:<9}{config:<7}{n:>5}{hv_mean:>9.3f}{hv_std:>8.3f}{hv_best:>9.3f}"
              f"{hv_worst:>9.3f}{trade_offs:>11.1f}{seconds:>9.2f}")

    with open(results_dir / "summary.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "instance", "config", "runs", "hv_mean", "hv_std", "hv_best", "hv_worst",
                         "mean_trade_offs", "mean_seconds"])
        writer.writerows(table)

    # Paired by seed because both algorithms use the same seeds and common experimental conditions.
    stat_rows = []
    algorithms = sorted({key[0] for key in grouped})
    if len(algorithms) == 2:
        a, b = algorithms
        combinations = sorted({(key[1], key[2]) for key in grouped})
        for instance, config in combinations:
            va = {seed: hv for seed, hv, _, _ in grouped.get((a, instance, config), [])}
            vb = {seed: hv for seed, hv, _, _ in grouped.get((b, instance, config), [])}
            common = sorted(set(va) & set(vb))
            if len(common) >= 2:
                statistic, p_value = paired_wilcoxon([va[s] for s in common], [vb[s] for s in common])
                stat_rows.append([instance, config, a, b, len(common), statistic, p_value])

    with open(results_dir / "statistics.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["instance", "config", "algorithm_a", "algorithm_b", "paired_runs",
                         "wilcoxon_statistic", "p_value_two_sided"])
        writer.writerows(stat_rows)

    with open(results_dir / "normalization.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["instance", "ideal_f1", "ideal_f2", "nadir_f1", "nadir_f2", "reference_f1", "reference_f2"])
        for instance, (ideal, nadir) in sorted(scale.items()):
            writer.writerow([instance, ideal[0], ideal[1], nadir[0], nadir[1], *REFERENCE_POINT])


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
    parser.add_argument("--representation", choices=["binary", "integer"], default="binary",
                        help="how a solution is stored (default: binary; integer results go to results/integer/)")
    args = parser.parse_args()

    configs = [config for config in CONFIGS if config.name in args.configs]
    results_dir = RESULTS_DIR if args.representation == "binary" else RESULTS_DIR / "integer"
    results_dir.mkdir(parents=True, exist_ok=True)
    rows = []  # one row per point of every final front
    # several instances or configs: each window closes by itself, so the next one can start
    close_windows = len(args.instances) * len(configs) > 1

    with ProcessPoolExecutor() as pool:  # one process per CPU core, so runs happen at the same time
        for instance_name in args.instances:
            instance = load_by_name(instance_name)
            print(f"\nloading {instance_name}: {instance.m} facilities, {instance.n} customers", flush=True)
            for config in configs:
                print(f"{instance_name}, {config.name}: {args.runs} runs of {' and '.join(args.algorithms)} at the same "
                      f"time ({args.representation}, population {config.pop_size}, "
                      f"{config.max_evaluations:,} evaluations each)", flush=True)
                first_runs = run_combination(pool, instance_name, config, args.algorithms, args.runs, rows,
                                             close_windows, args.representation)
                if first_runs:
                    save_checkpoint(rows, instance_name, config.name, first_runs, results_dir)

    if rows:
        summarise(rows, results_dir)
    folder = results_dir.relative_to(RESULTS_DIR.parent)
    print(f"\ndone: {folder}/fronts.csv, {folder}/run_metrics.csv, {folder}/summary.csv, "
          f"{folder}/statistics.csv, {folder}/normalization.csv and pictures in {folder}/plots/")


if __name__ == "__main__":
    main()
