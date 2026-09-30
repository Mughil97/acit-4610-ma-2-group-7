"""Entry point: run both MOEAs on every instance, config and seed, then
write metrics, statistical tests and plots to results/."""

import argparse

from app.algorithms import available_algorithms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--algorithms", nargs="+", choices=available_algorithms(), default=available_algorithms())
    parser.add_argument("--instances", nargs="+", help="Instance names, e.g. cap41 cap101 cap121")
    parser.add_argument("--configs", nargs="+", help="Config names, e.g. C1 C2 C3")
    parser.add_argument("--runs", type=int, help="Independent runs per combination")
    parser.parse_args()
    raise NotImplementedError


if __name__ == "__main__":
    main()
