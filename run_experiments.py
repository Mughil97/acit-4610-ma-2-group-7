"""Entry point: run the MOEAs on every instance, config and seed, and save the final fronts to results/fronts.csv.

Examples:
    python run_experiments.py                                                    # everything, 10 runs each
    python run_experiments.py --algorithms vega --instances cap121 --configs C1 --runs 1

Metrics (hypervolume), statistical tests and plots will be added here once app/utils has them.
"""

import argparse
import csv
import time

from app.algorithms import available_algorithms, create_algorithm
from app.config import BASE_SEED, CONFIGS, INSTANCES, N_RUNS, RESULTS_DIR
from app.problem.loader import load_by_name

ALL_INSTANCES = [name for names in INSTANCES.values() for name in names]
ALL_CONFIGS = [config.name for config in CONFIGS]


def run_once(algorithm, instance, config, seed, rows):
    """Run once, print one line and add the front to rows; return False if it can not run."""
    start = time.perf_counter()
    try:
        front = create_algorithm(algorithm, instance, config, seed).run()
    except NotImplementedError:
        print(f"{algorithm} {instance.name}: skipped, {algorithm} is not implemented yet")
        return False
    except ValueError as error:  # e.g. cap41/cap42 can not be solved
        print(f"{algorithm}: skipped, {error}")
        return False
    seconds = time.perf_counter() - start

    print(f"{algorithm:<6} {instance.name:<7} {config.name}  seed {seed}:  {len(front)} trade-offs,"
          f"  best f1 {front[0][0]:>9,.0f},  best f2 {front[-1][1]:>12,.0f},  {seconds:.2f} s")
    for f1, f2 in front:
        rows.append([algorithm, instance.name, config.name, seed, round(seconds, 3), f1, f2])
    return True


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

    for algorithm in args.algorithms:
        for instance_name in args.instances:
            instance = load_by_name(instance_name)
            can_run = True  # False once this algorithm fails on this instance
            for config in configs:
                for run in range(args.runs):
                    seed = BASE_SEED + run  # run 1 uses seed 42, run 2 uses seed 43, ...
                    if can_run:
                        can_run = run_once(algorithm, instance, config, seed, rows)

    RESULTS_DIR.mkdir(exist_ok=True)  # every front point, for the metrics and plots later
    out_path = RESULTS_DIR / "fronts.csv"
    with open(out_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["algorithm", "instance", "config", "seed", "seconds", "f1", "f2"])
        writer.writerows(rows)
    print(f"\nsaved {len(rows)} front points to {out_path}")


if __name__ == "__main__":
    main()
