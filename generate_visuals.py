"""
Report-ready visualisations for ACIT4610 Assignment 2.

Place this file in the project root, beside run_experiments.py, then run:

    python generate_visuals.py

Required inputs:
    results/run_metrics.csv
    results/summary.csv
    results/fronts.csv

Outputs:
    results/visuals_improved/

Design choices:
- Color-blind-friendly algorithm colors (Okabe-Ito palette).
- Cividis heatmap for sequential Hypervolume advantage.
- Shapes/linestyles as well as color for Pareto plots.
- Mean shown as a diamond and median as a line in boxplots.
- High-resolution PNG + vector SVG output for report use.
- Same seed for direct Pareto comparisons.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

# Windows/headless-safe: save figures directly instead of opening GUI windows.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter


# ---------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------

RESULTS_DIR = Path("results")
OUT_DIR = RESULTS_DIR / "visuals_improved"

INSTANCE_ORDER = ["cap61", "cap62", "cap101", "cap102", "cap121", "cap122"]
CONFIG_ORDER = ["C1", "C2", "C3"]
ALGORITHM_ORDER = ["vega", "nsga2"]

DISPLAY_NAME = {
    "vega": "VEGA",
    "nsga2": "NSGA-II",
}

# Okabe-Ito color-blind-friendly colors.
ALGORITHM_COLOR = {
    "vega": "#D55E00",   # vermillion
    "nsga2": "#0072B2",  # blue
}

# Different markers/linestyles also make plots readable in grayscale.
ALGORITHM_MARKER = {
    "vega": "o",
    "nsga2": "^",
}

ALGORITHM_LINESTYLE = {
    "vega": "--",
    "nsga2": "-",
}

# Same seed for both algorithms for a direct single-run Pareto comparison.
PARETO_SEED = 42

# Save raster + vector version.
SAVE_FORMATS = ("png", "svg")
PNG_DPI = 300

WITH_COMMAS = FuncFormatter(lambda value, _: f"{value:,.0f}")


# ---------------------------------------------------------------------
# GLOBAL REPORT STYLE
# ---------------------------------------------------------------------

plt.rcParams.update(
    {
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "legend.fontsize": 10.5,
        "figure.titlesize": 15,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing {path}.\n"
            "Run the experiments first:\n"
            "    python run_experiments.py --representation binary"
        )

    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def to_float(value) -> float:
    return float(value)


def to_int(value) -> int:
    return int(float(value))


def save_figure(fig, stem: str) -> None:
    """Save each figure as high-resolution PNG and vector SVG."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for ext in SAVE_FORMATS:
        kwargs = {"bbox_inches": "tight"}
        if ext == "png":
            kwargs["dpi"] = PNG_DPI
        fig.savefig(OUT_DIR / f"{stem}.{ext}", **kwargs)

    plt.close(fig)


def add_light_y_grid(ax) -> None:
    ax.set_axisbelow(True)
    ax.grid(axis="y", linestyle=":", linewidth=0.8, alpha=0.35)


def add_light_xy_grid(ax) -> None:
    ax.set_axisbelow(True)
    ax.grid(linestyle=":", linewidth=0.8, alpha=0.30)


# ---------------------------------------------------------------------
# PARETO HELPERS
# ---------------------------------------------------------------------

def dominates(a, b) -> bool:
    """Minimization: a dominates b if no worse in both and better in >=1."""
    return (
        a[0] <= b[0]
        and a[1] <= b[1]
        and (a[0] < b[0] or a[1] < b[1])
    )


def non_dominated_points(points):
    """Return unique non-dominated (f1, f2) points, sorted by f1."""
    unique = sorted(set(points))
    result = []

    for i, p in enumerate(unique):
        if not any(
            i != j and dominates(q, p)
            for j, q in enumerate(unique)
        ):
            result.append(p)

    return sorted(result, key=lambda x: (x[0], x[1]))


# ---------------------------------------------------------------------
# 1. HYPERVOLUME BOXPLOTS
# ---------------------------------------------------------------------

def make_hv_boxplots(run_rows):
    """
    One PNG/SVG per instance.

    Interpretation:
    - line inside box = median
    - diamond = mean
    - box = middle 50% (Q1 to Q3)
    - whiskers = non-outlier range
    - circles = outliers
    """
    grouped = defaultdict(list)

    for r in run_rows:
        grouped[
            (r["instance"], r["config"], r["algorithm"])
        ].append(to_float(r["hypervolume"]))

    for instance in INSTANCE_ORDER:
        data = []
        labels = []
        algorithms_for_box = []

        for config in CONFIG_ORDER:
            for algorithm in ALGORITHM_ORDER:
                values = grouped.get((instance, config, algorithm), [])
                if values:
                    data.append(values)
                    labels.append(f"{config}\n{DISPLAY_NAME[algorithm]}")
                    algorithms_for_box.append(algorithm)

        if not data:
            continue

        fig, ax = plt.subplots(figsize=(10.5, 6.3))

        bp = ax.boxplot(
            data,
            tick_labels=labels,
            patch_artist=True,
            showmeans=True,
            meanline=False,
            meanprops={
                "marker": "D",
                "markerfacecolor": "white",
                "markeredgecolor": "black",
                "markersize": 5.5,
            },
            medianprops={
                "color": "black",
                "linewidth": 1.7,
            },
            whiskerprops={
                "color": "#555555",
                "linewidth": 1.2,
            },
            capprops={
                "color": "#555555",
                "linewidth": 1.2,
            },
            flierprops={
                "marker": "o",
                "markerfacecolor": "none",
                "markeredgecolor": "#444444",
                "markersize": 5,
            },
        )

        for box, algorithm in zip(bp["boxes"], algorithms_for_box):
            box.set_facecolor(ALGORITHM_COLOR[algorithm])
            box.set_alpha(0.55)
            box.set_edgecolor("#333333")
            box.set_linewidth(1.1)

        ax.set_title(f"Hypervolume distribution over 10 independent runs — {instance}")
        ax.set_xlabel("Configuration and algorithm")
        ax.set_ylabel("Hypervolume (higher is better)")
        add_light_y_grid(ax)

        legend_handles = [
            Patch(
                facecolor=ALGORITHM_COLOR["vega"],
                edgecolor="#333333",
                alpha=0.55,
                label="VEGA",
            ),
            Patch(
                facecolor=ALGORITHM_COLOR["nsga2"],
                edgecolor="#333333",
                alpha=0.55,
                label="NSGA-II",
            ),
            Line2D(
                [0],
                [0],
                marker="D",
                color="none",
                markerfacecolor="white",
                markeredgecolor="black",
                markersize=6,
                label="Mean",
            ),
            Line2D(
                [0],
                [0],
                color="black",
                linewidth=1.7,
                label="Median",
            ),
        ]
        ax.legend(
            handles=legend_handles,
            loc="best",
            frameon=False,
            ncol=2,
        )

        fig.tight_layout()
        save_figure(fig, f"01_hv_boxplot_{instance}")


# ---------------------------------------------------------------------
# 2. MEAN HV + STANDARD DEVIATION
# ---------------------------------------------------------------------

def make_hv_mean_bars(summary_rows):
    """
    One PNG/SVG per instance.
    Bar height = mean HV.
    Error bar = standard deviation over 10 runs.
    """
    lookup = {
        (r["instance"], r["config"], r["algorithm"]): r
        for r in summary_rows
    }

    width = 0.34

    for instance in INSTANCE_ORDER:
        x = list(range(len(CONFIG_ORDER)))

        values = {}
        stds = {}

        for algorithm in ALGORITHM_ORDER:
            values[algorithm] = []
            stds[algorithm] = []

            for config in CONFIG_ORDER:
                row = lookup.get((instance, config, algorithm))
                values[algorithm].append(
                    to_float(row["hv_mean"]) if row else math.nan
                )
                stds[algorithm].append(
                    to_float(row["hv_std"]) if row else 0.0
                )

        fig, ax = plt.subplots(figsize=(9.2, 6.1))

        offsets = {
            "vega": -width / 2,
            "nsga2": width / 2,
        }

        for algorithm in ALGORITHM_ORDER:
            bars = ax.bar(
                [i + offsets[algorithm] for i in x],
                values[algorithm],
                width,
                yerr=stds[algorithm],
                capsize=4,
                label=DISPLAY_NAME[algorithm],
                color=ALGORITHM_COLOR[algorithm],
                alpha=0.82,
                edgecolor="#333333",
                linewidth=0.8,
            )

            ax.bar_label(
                bars,
                labels=[
                    f"{v:.3f}" if not math.isnan(v) else ""
                    for v in values[algorithm]
                ],
                padding=4,
                fontsize=9,
            )

        ax.set_xticks(x)
        ax.set_xticklabels(CONFIG_ORDER)
        ax.set_title(f"Mean Hypervolume ± standard deviation — {instance}")
        ax.set_xlabel("Configuration")
        ax.set_ylabel("Mean Hypervolume (higher is better)")
        add_light_y_grid(ax)
        ax.legend(frameon=False)

        # Give labels a little headroom.
        ymax = max(
            v + s
            for algorithm in ALGORITHM_ORDER
            for v, s in zip(values[algorithm], stds[algorithm])
            if not math.isnan(v)
        )
        ymin = min(
            v - s
            for algorithm in ALGORITHM_ORDER
            for v, s in zip(values[algorithm], stds[algorithm])
            if not math.isnan(v)
        )
        span = max(ymax - ymin, 0.01)
        ax.set_ylim(max(0, ymin - 0.12 * span), ymax + 0.18 * span)

        fig.tight_layout()
        save_figure(fig, f"02_hv_mean_error_{instance}")


# ---------------------------------------------------------------------
# 3. HV ADVANTAGE HEATMAP
# ---------------------------------------------------------------------

def make_hv_gain_heatmap(summary_rows):
    """
    Cell value = NSGA-II mean HV - VEGA mean HV.

    Positive value:
        NSGA-II has higher mean HV.

    Negative value:
        VEGA has higher mean HV.

    The current results are all positive, so a sequential Cividis palette
    is appropriate and color-blind friendly.
    """
    lookup = {
        (r["instance"], r["config"], r["algorithm"]):
            to_float(r["hv_mean"])
        for r in summary_rows
    }

    matrix = []

    for instance in INSTANCE_ORDER:
        row = []

        for config in CONFIG_ORDER:
            nsga = lookup.get((instance, config, "nsga2"))
            vega = lookup.get((instance, config, "vega"))

            if nsga is None or vega is None:
                row.append(float("nan"))
            else:
                row.append(nsga - vega)

        matrix.append(row)

    finite_values = [
        value
        for row in matrix
        for value in row
        if not math.isnan(value)
    ]

    if not finite_values:
        return

    vmin = min(finite_values)
    vmax = max(finite_values)

    # Avoid a zero-width scale in the unlikely case all values are equal.
    if math.isclose(vmin, vmax):
        vmax = vmin + 1e-9

    fig, ax = plt.subplots(figsize=(8.6, 7.2))

    image = ax.imshow(
        matrix,
        aspect="auto",
        cmap="cividis",
        vmin=vmin,
        vmax=vmax,
    )

    ax.set_xticks(range(len(CONFIG_ORDER)))
    ax.set_xticklabels(CONFIG_ORDER)
    ax.set_yticks(range(len(INSTANCE_ORDER)))
    ax.set_yticklabels(INSTANCE_ORDER)

    ax.set_xlabel("Configuration")
    ax.set_ylabel("Benchmark instance")
    ax.set_title(
        "Mean Hypervolume advantage of NSGA-II over VEGA\n"
        "NSGA-II mean HV − VEGA mean HV"
    )

    # Draw subtle cell boundaries.
    ax.set_xticks(
        [x - 0.5 for x in range(1, len(CONFIG_ORDER))],
        minor=True,
    )
    ax.set_yticks(
        [y - 0.5 for y in range(1, len(INSTANCE_ORDER))],
        minor=True,
    )
    ax.grid(
        which="minor",
        color="white",
        linestyle="-",
        linewidth=1.0,
        alpha=0.35,
    )
    ax.tick_params(which="minor", bottom=False, left=False)

    # Dynamic text color based on the actual mapped background luminance.
    cmap = plt.get_cmap("cividis")

    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if math.isnan(value):
                continue

            norm_value = (value - vmin) / (vmax - vmin)
            r, g, b, _ = cmap(norm_value)

            # Relative luminance approximation.
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            text_color = "black" if luminance > 0.55 else "white"

            ax.text(
                j,
                i,
                f"{value:+.3f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=11,
                fontweight="semibold",
            )

    cbar = fig.colorbar(
        image,
        ax=ax,
        fraction=0.046,
        pad=0.04,
    )
    cbar.set_label("Difference in mean Hypervolume")

    fig.tight_layout()
    save_figure(fig, "03_hv_gain_heatmap_all_instances")


# ---------------------------------------------------------------------
# 4A. PARETO FRONT — SAME SEED
# ---------------------------------------------------------------------

def make_pareto_seed_plots(front_rows):
    """
    One plot for every instance/configuration using the SAME seed
    for both VEGA and NSGA-II.

    This is the cleanest direct single-run comparison.
    """
    grouped = defaultdict(list)

    for r in front_rows:
        seed = to_int(r["seed"])

        if seed != PARETO_SEED:
            continue

        grouped[
            (r["instance"], r["config"], r["algorithm"])
        ].append(
            (to_float(r["f1"]), to_float(r["f2"]))
        )

    for instance in INSTANCE_ORDER:
        for config in CONFIG_ORDER:
            fig, ax = plt.subplots(figsize=(8.4, 6.3))
            found = False

            for algorithm in ALGORITHM_ORDER:
                points = sorted(
                    grouped.get((instance, config, algorithm), []),
                    key=lambda p: (p[0], p[1]),
                )

                if not points:
                    continue

                found = True

                ax.plot(
                    [p[0] for p in points],
                    [p[1] for p in points],
                    marker=ALGORITHM_MARKER[algorithm],
                    linestyle=ALGORITHM_LINESTYLE[algorithm],
                    color=ALGORITHM_COLOR[algorithm],
                    linewidth=1.8,
                    markersize=5.5,
                    markerfacecolor="white",
                    markeredgewidth=1.2,
                    label=f"{DISPLAY_NAME[algorithm]} ({len(points)} points)",
                )

            if not found:
                plt.close(fig)
                continue

            ax.set_title(
                f"Final Pareto-front comparison — {instance}, {config}, "
                f"seed {PARETO_SEED}"
            )
            ax.set_xlabel("f1: facility-opening cost (minimize)")
            ax.set_ylabel("f2: customer-allocation cost (minimize)")
            ax.xaxis.set_major_formatter(WITH_COMMAS)
            ax.yaxis.set_major_formatter(WITH_COMMAS)
            add_light_xy_grid(ax)
            ax.legend(frameon=False)

            # Helpful directional note without overstating a single 'best' point.
            ax.text(
                0.015,
                0.02,
                "Lower-left indicates lower values for both objectives",
                transform=ax.transAxes,
                fontsize=9,
                color="#555555",
                va="bottom",
            )

            fig.tight_layout()
            save_figure(
                fig,
                f"04a_pareto_seed{PARETO_SEED}_{instance}_{config}",
            )


# ---------------------------------------------------------------------
# 4B. POOLED NON-DOMINATED FRONT ACROSS ALL RUNS
# ---------------------------------------------------------------------

def make_pareto_pooled_plots(front_rows):
    """
    Pool final-front points from all 10 runs and retain only the
    non-dominated union for each algorithm.

    This is a supplementary all-runs envelope, NOT a single-run front.
    """
    grouped = defaultdict(list)

    for r in front_rows:
        grouped[
            (r["instance"], r["config"], r["algorithm"])
        ].append(
            (to_float(r["f1"]), to_float(r["f2"]))
        )

    for instance in INSTANCE_ORDER:
        for config in CONFIG_ORDER:
            fig, ax = plt.subplots(figsize=(8.4, 6.3))
            found = False

            for algorithm in ALGORITHM_ORDER:
                all_points = grouped.get(
                    (instance, config, algorithm),
                    [],
                )

                if not all_points:
                    continue

                points = non_dominated_points(all_points)
                found = True

                ax.plot(
                    [p[0] for p in points],
                    [p[1] for p in points],
                    marker=ALGORITHM_MARKER[algorithm],
                    linestyle=ALGORITHM_LINESTYLE[algorithm],
                    color=ALGORITHM_COLOR[algorithm],
                    linewidth=1.8,
                    markersize=5.5,
                    markerfacecolor="white",
                    markeredgewidth=1.2,
                    label=(
                        f"{DISPLAY_NAME[algorithm]} "
                        f"({len(points)} pooled ND points)"
                    ),
                )

            if not found:
                plt.close(fig)
                continue

            ax.set_title(
                f"Pooled non-dominated trade-off envelope — "
                f"{instance}, {config}\nAll 10 runs combined"
            )
            ax.set_xlabel("f1: facility-opening cost (minimize)")
            ax.set_ylabel("f2: customer-allocation cost (minimize)")
            ax.xaxis.set_major_formatter(WITH_COMMAS)
            ax.yaxis.set_major_formatter(WITH_COMMAS)
            add_light_xy_grid(ax)
            ax.legend(frameon=False)

            ax.text(
                0.015,
                0.02,
                "Supplementary plot: non-dominated union across all runs",
                transform=ax.transAxes,
                fontsize=9,
                color="#555555",
                va="bottom",
            )

            fig.tight_layout()
            save_figure(
                fig,
                f"04b_pareto_pooled_{instance}_{config}",
            )


# ---------------------------------------------------------------------
# 5. MEAN NUMBER OF NON-DOMINATED SOLUTIONS
# ---------------------------------------------------------------------

def make_tradeoff_bars(summary_rows):
    """
    One PNG/SVG per instance.
    Uses summary.csv mean_trade_offs.
    """
    lookup = {
        (r["instance"], r["config"], r["algorithm"]): r
        for r in summary_rows
    }

    width = 0.34

    for instance in INSTANCE_ORDER:
        x = list(range(len(CONFIG_ORDER)))

        values = {}

        for algorithm in ALGORITHM_ORDER:
            values[algorithm] = []

            for config in CONFIG_ORDER:
                row = lookup.get((instance, config, algorithm))
                values[algorithm].append(
                    to_float(row["mean_trade_offs"])
                    if row
                    else math.nan
                )

        fig, ax = plt.subplots(figsize=(9.2, 6.1))

        offsets = {
            "vega": -width / 2,
            "nsga2": width / 2,
        }

        for algorithm in ALGORITHM_ORDER:
            bars = ax.bar(
                [i + offsets[algorithm] for i in x],
                values[algorithm],
                width,
                label=DISPLAY_NAME[algorithm],
                color=ALGORITHM_COLOR[algorithm],
                alpha=0.82,
                edgecolor="#333333",
                linewidth=0.8,
            )

            ax.bar_label(
                bars,
                labels=[
                    f"{v:.1f}" if not math.isnan(v) else ""
                    for v in values[algorithm]
                ],
                padding=3,
                fontsize=9.5,
            )

        ax.set_xticks(x)
        ax.set_xticklabels(CONFIG_ORDER)
        ax.set_title(
            f"Mean number of final non-dominated solutions — {instance}"
        )
        ax.set_xlabel("Configuration")
        ax.set_ylabel("Mean non-dominated solutions")
        add_light_y_grid(ax)
        ax.legend(frameon=False)

        ymax = max(
            value
            for algorithm in ALGORITHM_ORDER
            for value in values[algorithm]
            if not math.isnan(value)
        )
        ax.set_ylim(0, ymax * 1.16)

        fig.tight_layout()
        save_figure(fig, f"05_mean_tradeoffs_{instance}")


# ---------------------------------------------------------------------
# 6. RUNTIME
# ---------------------------------------------------------------------

def make_runtime_lines(summary_rows):
    """
    One PNG/SVG per instance.
    Shows mean runtime under C1/C2/C3.
    """
    lookup = {
        (r["instance"], r["config"], r["algorithm"]): r
        for r in summary_rows
    }

    x = list(range(len(CONFIG_ORDER)))

    for instance in INSTANCE_ORDER:
        fig, ax = plt.subplots(figsize=(9.2, 6.1))

        for algorithm in ALGORITHM_ORDER:
            seconds = []

            for config in CONFIG_ORDER:
                row = lookup.get((instance, config, algorithm))
                seconds.append(
                    to_float(row["mean_seconds"])
                    if row
                    else math.nan
                )

            ax.plot(
                x,
                seconds,
                marker=ALGORITHM_MARKER[algorithm],
                linestyle=ALGORITHM_LINESTYLE[algorithm],
                color=ALGORITHM_COLOR[algorithm],
                linewidth=2.0,
                markersize=7,
                markerfacecolor="white",
                markeredgewidth=1.4,
                label=DISPLAY_NAME[algorithm],
            )

            for xi, sec in zip(x, seconds):
                if not math.isnan(sec):
                    ax.annotate(
                        f"{sec:.2f}s",
                        (xi, sec),
                        textcoords="offset points",
                        xytext=(0, 8),
                        ha="center",
                        fontsize=9,
                    )

        ax.set_xticks(x)
        ax.set_xticklabels(CONFIG_ORDER)
        ax.set_title(f"Mean execution time — {instance}")
        ax.set_xlabel("Configuration")
        ax.set_ylabel("Mean execution time (seconds)")
        add_light_y_grid(ax)
        ax.legend(frameon=False)

        fig.tight_layout()
        save_figure(fig, f"06_runtime_{instance}")


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    run_rows = read_csv(RESULTS_DIR / "run_metrics.csv")
    summary_rows = read_csv(RESULTS_DIR / "summary.csv")
    front_rows = read_csv(RESULTS_DIR / "fronts.csv")

    print("Generating improved report-ready visualisations...")

    make_hv_boxplots(run_rows)
    print("  ✓ Hypervolume boxplots")

    make_hv_mean_bars(summary_rows)
    print("  ✓ Mean HV + standard-deviation charts")

    make_hv_gain_heatmap(summary_rows)
    print("  ✓ Color-blind-friendly HV advantage heatmap")

    make_pareto_seed_plots(front_rows)
    print(f"  ✓ Same-seed Pareto plots (seed {PARETO_SEED})")

    make_pareto_pooled_plots(front_rows)
    print("  ✓ Pooled Pareto trade-off envelopes")

    make_tradeoff_bars(summary_rows)
    print("  ✓ Mean non-dominated-solution charts")

    make_runtime_lines(summary_rows)
    print("  ✓ Runtime charts")

    print(f"\nDone. Visuals saved in:\n  {OUT_DIR.resolve()}")
    print("\nEach figure is saved as both PNG and SVG.")
    print("\nRecommended report figures to inspect first:")
    print("  03_hv_gain_heatmap_all_instances")
    print("  01_hv_boxplot_cap121")
    print(f"  04a_pareto_seed{PARETO_SEED}_cap61_C2")
    print(f"  04a_pareto_seed{PARETO_SEED}_cap101_C2")
    print(f"  04a_pareto_seed{PARETO_SEED}_cap121_C2")
    print("  05_mean_tradeoffs_cap121")
    print("  06_runtime_cap121")


if __name__ == "__main__":
    main()
