# VEGA with Binary Representation for CFLP

Group 7 — ACIT4610 Evolutionary Artificial Intelligence and Robotics

This folder contains a standalone VEGA implementation for the multi-objective capacitated facility location problem. It minimizes facility-opening cost and customer-allocation cost separately, using OR-Library benchmark data. The evolutionary logic is implemented explicitly in Python.

## Files

- `vega.py`: data loading, representation, feasibility repair/decoding, objective evaluation, VEGA and command-line execution.
- `data/`: cap61, cap62, cap101, cap102, cap121 and cap122 data files.
- `summarize_results.py`: optional CSV summaries and SVG plots from saved runs.
- `plot_comparisons.py`: optional PNG/JPG figures from saved runs.
- `plot_evolution.py`: optional PNG/JPG figures showing the evolution of one binary VEGA run.
- `requirements.txt`: optional plotting dependency, Pillow.

Keep `data/` beside `vega.py`. Other algorithm files are not required to run VEGA.

## Requirements

Python 3.10 or later is recommended. The algorithm and CSV summarizer use only the Python standard library; they do not import NumPy, pandas or Matplotlib.

For optional PNG/JPG figures:

```powershell
py -m pip install pillow
```

Pillow is needed only for plotting. On macOS/Linux replace `py` with `python3`.

## Representation and feasibility

Each chromosome is an immutable tuple with one bit per candidate facility: `1` means open and `0` means closed. The decoder processes customers by decreasing demand, breaking ties by customer index. It assigns each customer to the cheapest open facility with sufficient remaining capacity. If none fits, it opens a fitting closed facility, choosing by allocation cost, then fixed opening cost, then facility index. Repaired opening bits are inherited. Open but unused facilities still contribute to opening cost.

Initialization samples each opening bit independently with probability 0.5. Uniform crossover exchanges corresponding bits with probability 0.5 when crossover is applied. A mutation event flips one randomly selected opening bit.

Every customer is assigned wholly to one facility and facility capacities must be respected. If no fitting facility remains, the procedure raises an error instead of returning an overloaded solution. Greedy failure does not establish global infeasibility.

## Objectives and data

For facility opening decisions `y_i` and customer assignments `x_ij`:

- Opening cost: `f1 = sum(F_i * y_i)`.
- Allocation cost: `f2 = sum(C_ij * x_ij)`.

`F_i` comes from the facility fixed-cost field; capacities come from the capacity field. Customer records supply demand and the cost of allocating each customer's entire demand to each facility. `C_ij` is used directly; it is not multiplied by demand again. Dataset values are not generated or modified.

Data source: [OR-Library capacitated warehouse location benchmarks](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/capinfo.html).

## VEGA design

VEGA uses objective-specific selection and non-elitist population replacement. At each generation:

1. Shuffle the population and divide it into two equal groups, one for each objective.
2. Within each group, select parents with replacement by roulette-wheel selection. For objective value `f`, the selection weight is `1 / (1 + f)`, so lower costs receive larger weights.
3. Combine and shuffle the selected parents, then pair them consecutively.
4. Apply uniform crossover and single-bit mutation, and decode/repair every offspring before evaluating its two objectives.
5. Replace the entire population with the offspring. Stop when the objective-evaluation budget is reached.

VEGA does not use Pareto ranks or an elitist archive during evolution. After termination, extract distinct non-dominated objective pairs from the final population for reporting and hypervolume calculation. This final filtering does not change VEGA's non-elitist replacement.

## Configurations

| Configuration | Population size | Crossover probability | Mutation probability | Evaluation budget |
|---|---:|---:|---:|---:|
| C1 | 40 | 0.8 | 0.1 | 12,000 |
| C2 | 60 | 0.8 | 0.1 | 12,000 |
| C3 | 60 | 0.8 | 0.2 | 12,000 |

Mutation probability is per chromosome. Initialization is included in the evaluation budget. Full runs use seeds 42–51. Six instances × three configurations × ten seeds give 180 VEGA runs. Runtime includes initialization and evolution, excluding output writing and plotting.

## Run one full experiment

Open a terminal in this folder:

```powershell
py vega.py --instance cap61 --config C1 --seed 42
```

For another instance/configuration:

```powershell
py vega.py --instance cap121 --config C3 --seed 42
```

A short installation check uses a separate results folder:

```powershell
py vega.py --instance cap61 --config C1 --seed 42 --budget 400 --output quick_results
```

Do not mix short validation runs with full experimental results.

## Run all 180 VEGA experiments in PowerShell

```powershell
$instances = @("cap61", "cap62", "cap101", "cap102", "cap121", "cap122")
$configs = @("C1", "C2", "C3")
foreach ($instance in $instances) {
    foreach ($config in $configs) {
        foreach ($seed in 42..51) {
            py vega.py --instance $instance --config $config --seed $seed
            if ($LASTEXITCODE -ne 0) { throw "VEGA run failed: $instance $config $seed" }
        }
    }
}
```

Add `--skip-existing` to the algorithm command to resume matching saved runs. A settings mismatch is rejected. Keep an output directory tied to a specific code version; do not edit evolutionary logic and reuse its old results.

## Outputs and figures

Each run writes a JSON file such as `results/vega/cap61_C1_42.json`, containing settings, data hash, evaluation count, runtime, non-dominated count and final assignments/objectives.

If the optional summary and plotting scripts are included:

```powershell
py summarize_results.py
py plot_comparisons.py
```

CSV summaries are saved in `results/summaries/`. PNG/JPG charts are saved in:

- `results/summaries/comparison_plots/png/`
- `results/summaries/comparison_plots/jpg/`

A folder containing only VEGA runs produces only VEGA results. Cross-algorithm comparisons require the other algorithms' results under matched settings.

## Plot one run's evolution

Keep `plot_evolution.py` beside `vega.py` and install Pillow as described above. Run:

```powershell
py plot_evolution.py --algorithm vega --instance cap121 --config C3 --seed 42
```

Always specify `--algorithm vega` in this standalone folder. The script defaults to all three algorithms, which requires the VEGA and NSGA-II modules as well.

The script runs a new experiment to record its history; it does not reconstruct evolution from an existing final-results JSON file. It uses the selected configuration's 12,000-evaluation budget unless `--budget` is supplied. Recorded runs are separate from the benchmark results and should not be used for benchmark timing because history recording adds overhead.

The figure shows the initial and final objective distributions, changes in the best opening and allocation costs, and population diversity through generations. Both objectives are minimized. The best `f1` and best `f2` can belong to different solutions; one seed illustrates behaviour, while conclusions require the independent-run summaries.

Outputs for the example command:

- `results/evolution_plots/png/vega_cap121_C3_seed42.png`
- `results/evolution_plots/jpg/vega_cap121_C3_seed42.jpg`
- `results/evolution_plots/vega_cap121_C3_seed42_history.json`

Open the image folder in Windows:

```powershell
explorer.exe .\results\evolution_plots\png
```

This evolution script uses the binary decoder and initialization. It must be adapted before use with the integer implementation.

## Hypervolume and fair comparisons

The summary script calculates exact two-objective minimization HV using one reference point per instance, shared across the saved runs in that results folder. Each reference coordinate is the maximum saved objective value plus `max(1, 0.1 * observed_range)`. Costs are kept in raw units; larger HV is better.

Separate binary and integer summary folders can produce different references. Recalculate both representations' HV using a common reference per instance before comparing their values. Do not average raw HV across instance scales. Also use a common definition of non-dominated count, evaluation budget and timing environment.

Binary and integer implementations can differ in representation, repair, initialization and selection details. Their comparison evaluates complete implementations unless these other differences are controlled.

## Version

The standalone binary implementation identifies its output as `python-binary-v1`. Report the source revision, seeds and timing environment alongside experimental results.
