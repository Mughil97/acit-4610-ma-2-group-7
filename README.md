# ACIT4610 Project 2  - Group 7
##  Multi-Objective Evolutionary Optimisation for the Capacitated Facility Location Problem (CFLP)

## Project Overview

This project implements and compares two multi-objective evolutionary algorithms (MOEAs) for the Capacitated Facility Location Problem (CFLP):

- **VEGA** – Vector Evaluated Genetic Algorithm
- **NSGA-II** – Non-dominated Sorting Genetic Algorithm II

The CFLP is a combinatorial optimisation problem where the goal is to decide which facilities should be opened and how customers should be assigned to facilities while satisfying capacity constraints.

The problem involves conflicting objectives:

1. **Minimise facility opening cost**
2. **Minimise customer allocation cost**

Because improving one objective may negatively affect another, the solution is not a single optimal point but a set of **non-dominated trade-off solutions** represented by the Pareto front.

The algorithms are evaluated on benchmark instances from the [OR-Library](https://people.brunel.ac.uk/~mastjjb/jeb/orlib/capinfo.html) under the same representation, repair/decoding procedure, genetic operators, random seeds, evaluation budgets, and experimental conditions.

---

## Problem Description

The Capacitated Facility Location Problem consists of:

- A set of candidate facilities
- A set of customers
- Facility opening costs
- Facility capacity constraints
- Customer demands
- Customer-to-facility allocation costs

### Feasibility Requirements

- Every customer is assigned to exactly one facility
- Customers are only assigned to available facilities
- Facility capacity limitations are respected
- Objective values are calculated only after a feasible assignment has been produced

The challenge is balancing the two conflicting objectives:

### Objective 1: Facility Opening Cost

$\min f_1 = \sum_{i=1}^{m}F_i y_i$

where:

- Facilities $i=1,\ldots,m$
- $F_i$ is the fixed opening cost of facility $i$
- $y_i = 1$ if facility $i$ is open, otherwise $0$

### Objective 2: Customer Allocation Cost

$\min f_2 = \sum_{i=1}^{m}\sum_{j=1}^{n}C_{ij}x_{ij}$

where:

- Facilities $i=1,\ldots,m$
- Customers $j=1,\dots,n$
- $C_{ij}$ is the allocation cost of assigning customer $j$ to facility $i$
- $x_{ij} = 1$ if customer $j$ is assigned to facility $i$, otherwise $0$

The OR-Library allocation-cost values used by the project already include the demand contribution, so demand is **not multiplied into the allocation cost again**.

Both objectives are minimised simultaneously.

---

## Algorithms

### VEGA (Vector Evaluated Genetic Algorithm)

VEGA is a multi-objective evolutionary algorithm that separates selection according to individual objectives.

The population is divided according to objectives, where each subgroup is evaluated using one objective before recombination and mutation.

General Workflow:

```text
Population initialisation
        ↓
Objective evaluation
        ↓
Objective-specific selection
        ↓
Crossover
        ↓
Mutation
        ↓
Replacement
        ↓
Repeat
```

VEGA does not use Pareto ranking or crowding distance during its main selection process. Pareto dominance is used when extracting the final non-dominated solutions for evaluation and visualisation.

### NSGA-II (Non-dominated Sorting Genetic Algorithm II)

NSGA-II is a Pareto-based, elitist multi-objective evolutionary algorithm designed to maintain both convergence and diversity.

It uses:

- Non-dominated sorting
- Pareto-front rank
- Crowding distance
- Elitist environmental selection

General workflow:

```text
Initialise population
        ↓
Evaluate objectives
        ↓
Non-dominated sorting
        ↓
Calculate crowding distance
        ↓
Select parents
        ↓
Crossover and mutation
        ↓
Generate offspring
        ↓
Combine parents and offspring
        ↓
Non-dominated sorting
        ↓
Add complete fronts in rank order
        ↓
If the next front does not completely fit:
keep solutions with the largest crowding distance
        ↓
Next generation
        ↓
Repeat
```

The implementation follows the standard NSGA-II environmental-selection procedure and does not apply an additional duplicate-chromosome filtering step before survivor selection. Solutions are selected primarily according to Pareto-front rank, while crowding distance is used to preserve diversity within the same front.

Both VEGA and NSGA-II are implemented under the same experimental framework, using the same representation, repair and decoding procedure, genetic operators, random seeds, and evaluation budgets to support a fair comparison.

---

## Solution Representation

The project uses a chromosome-based representation for evolutionary optimisation.

Each chromosome represents a candidate solution for the **Capacitated Facility Location Problem (CFLP)**. 
The evolutionary algorithms operate on chromosomes, while repair and decoding procedures 
transform these chromosomes into feasible CFLP solutions before objective evaluation.

The overall solution pipeline is:

```text
Chromosome
      ↓
Repair / Feasibility Handling
      ↓
Solution Decoding
      ↓
Objective Evaluation
      ↓
Evolutionary Selection
```

## Binary Chromosome Representation

The project uses a binary chromosome representation where each gene corresponds to one candidate facility.

Each gene has two possible values:

- `1` → the facility is opened
- `0` → the facility is closed

For a problem instance with `m` candidate facilities, the chromosome length is `m`.

Example:

```text
[1, 0, 1, 0, 0, 1]
```

represents:

```text
Facility 0 → Open
Facility 1 → Closed
Facility 2 → Open
Facility 3 → Closed
Facility 4 → Closed
Facility 5 → Open
```

The chromosome represents facility-opening decisions only. Customer-to-facility assignments are generated by the decoder.

### Shared Repair and Decoding

Evolutionary operators such as crossover and mutation may create infeasible solutions. 
Therefore, a repair procedure is applied before objective evaluation.

The repair and decoding process ensures that:

- the selected facilities provide sufficient capacity to satisfy total customer demand.
- each customer receives a feasible assignment.
- customers are assigned only to open facilities.
- facility capacity constraints are respected.

Both algorithms use the same problem-specific representation and feasibility logic:

```text
Binary chromosome
        ↓
Repair / feasibility handling
        ↓
Identify open facilities
        ↓
Assign customers to feasible open facilities
        ↓
Generate complete CFLP solution
        ↓
Evaluate f1 and f2
```

After decoding, the solution can be evaluated using the two objective functions:

1. Facility opening cost
2. Customer allocation cost

The same chromosome representation, repair mechanism, and objective evaluation procedure are used by both VEGA 
and NSGA-II to ensure a fair algorithm comparison.

---

## Benchmark Instances

The experiments use the following six OR-Library CFLP instances:

| Scale | Instances |
|---|---|
| Small | `cap61`, `cap62` |
| Medium | `cap101`, `cap102` |
| Large | `cap121`, `cap122` |

Each instance contains:

- Number of facilities
- Number of customers
- Facility capacities
- Facility opening costs
- Customer demands
- Customer-facility allocation costs

---

## Experimental Setup

Both algorithms are evaluated under the same conditions.

### Configurations

| Configuration | Population | Maximum Evaluations | Crossover Probability | Mutation Flips |
|---|---:|---:|---:|---:|
| C1 | 50 | 10,000 | 0.80 | 1 |
| C2 | 100 | 30,000 | 0.90 | 1 |
| C3 | 200 | 100,000 | 0.95 | 2 |

Each algorithm is run **10 independent times** for every instance/configuration combination.

The default seeds are shared between VEGA and NSGA-II so that the two algorithms are compared under matched stochastic runs.

With:

- 2 algorithms;
- 6 benchmark instances;
- 3 configurations;
- 10 independent runs;

the complete experiment consists of **360 algorithm runs**.

---

## Evaluation Metrics

Algorithms are compared using:

- **Hypervolume (HV)**
- **Number of non-dominated solutions**
- **Execution time**
- **Pareto-front plots**


### Hypervolume (HV)

Hypervolume measures the quality of the obtained non-dominated set by considering both convergence toward the Pareto front and the spread of solutions across the objective space.

It calculates the region of objective space dominated by the obtained solutions relative to a fixed reference point. Because both objectives are minimised, a **larger Hypervolume value indicates better overall performance**.

For each benchmark instance, VEGA and NSGA-II across all configurations use the same normalisation bounds and the same Hypervolume reference point to ensure a fair comparison.

The normalisation parameters and reference point used in the completed experiment are saved in:

```text
results/normalization.csv
```
### Number of Non-Dominated Solutions

The number of non-dominated solutions indicates how many alternative trade-off solutions are present in the final front.

A larger count alone does **not** prove that one algorithm is better; it is interpreted together with Hypervolume and Pareto-front coverage.

### Execution Time

Runtime is recorded for every run and summarised across the 10 independent runs.

### Statistical Comparison

Hypervolume values are statistically compared using a **paired two-sided Wilcoxon signed-rank test**.

Runs are paired by random seed so that VEGA and NSGA-II are compared using matched experimental conditions.

The statistical-test results are saved to:

```text
results/statistics.csv
```

---

## Repository Structure

```text
acit-4610-ma-2-group-7/
│
├── app/
│   ├── algorithms/
│   │   ├── base.py
│   │   ├── factory.py
│   │   ├── operators.py
│   │   ├── vega.py
│   │   └── nsga2.py
│   │
│   ├── problem/
│   │   ├── loader.py
│   │   ├── representation.py
│   │   ├── repair.py
│   │   └── evaluation.py
│   │
│   ├── utils/
│   │   ├── metrics.py
│   │   ├── pareto.py
│   │   ├── plotting.py
│   │   └── statistics.py
│   │
│   └── config.py
│
├── data/
│   └── CFLP benchmark instances
│
├── tests/
│   └── test_core.py
│
├── results/
│   ├── fronts.csv
│   ├── run_metrics.csv
│   ├── summary.csv
│   ├── statistics.csv
│   ├── normalization.csv
│   ├── plots/
│   └── visuals_improved/
│
├── generate_visuals_improved.py
├── run_experiments.py
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Mughil97/acit-4610-ma-2-group-7.git
```

Navigate to the project folder:

```bash
cd acit-4610-ma-2-group-7
```

## 2. Create and activate a virtual environment (recommended)

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment:

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows**

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```
The project uses:

```text
matplotlib
scipy
pytest
```
---

## Running Experiments

To run the experiment,

```bash
python run_experiments.py
```

The experiment runner uses a non-interactive Matplotlib backend so plots can be generated safely during parallel execution without opening GUI windows.

Progress for the first matched run is printed in the terminal, while the final result files and figures are saved automatically.

The generated outputs include:

- Objective values (`f1`, `f2`)
- Non-dominated solutions
- Pareto-front data and visualisations
- Hypervolume measurements
- Number of non-dominated trade-off solutions
- Runtime statistics
- paired Wilcoxon test results
- Hypervolume normalisation parameters

---
## Experiment Outputs

After a full run, the main output files are:

#### `results/fronts.csv`

Contains every point in every final non-dominated front:

```text
algorithm, instance, config, seed, seconds, f1, f2
```

#### `results/run_metrics.csv`

Contains one row per algorithm run:

```text
algorithm, instance, config, seed, hypervolume, non_dominated, seconds
```

#### `results/summary.csv`

Contains aggregate results for each algorithm/instance/configuration:

```text
algorithm
instance
config
runs
hv_mean
hv_std
hv_best
hv_worst
mean_trade_offs
mean_seconds
```
### `results/statistics.csv`

Contains the paired Wilcoxon comparison of Hypervolume:

```text
instance
config
algorithm_a
algorithm_b
paired_runs
wilcoxon_statistic
p_value_two_sided
```

### `results/normalization.csv`

Records the normalisation bounds and Hypervolume reference point used for each instance.

### `results/plots/`

Contains the standard experiment-run and Pareto-front plots generated by `run_experiments.py`.

---

## Running Tests

Run the test suite using:

```bash
python -m pytest -q
```

The core tests validate:

- Pareto dominance and non-dominated extraction;
- OR-Library instance loading;
- binary repair and assignment feasibility;
- matched binary initialisation for VEGA and NSGA-II under the same seed;
- NSGA-II non-dominated sorting and crowding distance;
- configured objective-evaluation budgets.

A successful run should report:

```text
6 passed
```

---
## Generating Report Visualisations

After the experiment finishes, generate the report-ready figures with:

```bash
python generate_visuals.py
```

The script reads the final CSV outputs and creates figures such as:

- mean Hypervolume comparisons;
- Hypervolume distributions;
- number of non-dominated trade-off solutions;
- execution-time comparisons;
- Pareto-front comparisons;
- Hypervolume-difference summaries.

The generated figures are saved under:

```text
results/visuals_improved/
```

---
## Reproducibility and Fair Comparison

The comparison is designed so that differences between VEGA and NSGA-II come from their multi-objective selection and survivor-selection mechanisms rather than from different problem handling.

Both algorithms therefore share:

- binary chromosome representation;
- initialisation procedure;
- random seeds;
- repair and decoding logic;
- objective evaluation;
- crossover operator;
- mutation operator;
- population size within each configuration;
- maximum objective-evaluation budget within each configuration;
- Hypervolume normalisation;
- Hypervolume reference point.

The principal algorithmic difference is how each method performs multi-objective selection and replacement.

## AI Use Disclosure

During the development of this project, generative AI tools, including ChatGPT (OpenAI) and Claude (Anthropic), were used as supporting tools for permitted coding-related activities.

The tools were used for:

Technical and coding clarification: Clarifying programming concepts, algorithm behaviour, and implementation requirements.

Project scaffolding: The project's directory structure and scaffolding with factory pattern was generated using AI.

Pair programming: Working interactively with AI as a virtual pair programmer to write and refine code for complex logic.

Data visualisation: Assisting with Python/Matplotlib code used to generate plots and visualise experimental results.

Code review and refactoring: Assisting with debugging and refactoring code for better performance, readability, and structure.

All algorithmic decisions, parameter choices, experiments, outputs, and final code were reviewed and verified by the group.

The final written report was produced by the group members in their own words in accordance with the assignment's AI-use requirements.
