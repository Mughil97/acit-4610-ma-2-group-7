# Project Workflow

**Course:** ACIT4610 Evolutionary Artificial Intelligence and Robotics  
**Project:** Multi-Objective Capacitated Facility Location Problem Using MOEAs  
**Group:** 7
**Algorithms:** NSGA-II and SPEA2  

---

## 1. Purpose

This document explains the **overall workflow of the project**: what happens, in what order, and how the major modules interact.

Detailed algorithm logic is kept separately in:

```text
docs/PSEUDOCODE.md
```

The project must compare NSGA-II and SPEA2 fairly. Therefore, both algorithms use the same:

- OR-Library benchmark instances;
- solution representation;
- initialization procedure;
- feasibility handling / repair;
- objective evaluation;
- crossover operator;
- mutation operator;
- parameter configuration;
- objective-evaluation budget; and
- random-seed scheme.

Only the multi-objective ranking, diversity handling, archive logic, and environmental selection differ.

---

# 2. Overall Project Flow

```text
PROJECT REQUIREMENTS
        ↓
OR-Library benchmark instances
        ↓
Load and validate data
        ↓
Define common CFLP representation
        ↓
Generate feasible initial population
        ↓
Shared feasibility checking / repair
        ↓
Evaluate f1 and f2
        ↓
Shared crossover + mutation
        ↓
        ┌──────────────────────────┐
        │                          │
     NSGA-II                    SPEA2
        │                          │
Non-dominated sorting       Strength
Crowding distance           Raw fitness
Tournament selection        Density
Elitist survival            External archive
        │                    Truncation
        │                          │
        └────────────┬─────────────┘
                     ↓
             Final Pareto sets
                     ↓
       Common normalization for HV
                     ↓
            Hypervolume (HV)
    Number of non-dominated solutions
            Execution time
                     ↓
          10 independent runs
                     ↓
      Mean / SD / Best / Worst HV
                     ↓
       Statistical comparison
                     ↓
       Pareto-front comparison plots
                     ↓
          Analysis and final report
```

---

# 3. Repository Flow (Proposed)

The repository is organized so that problem-specific logic is shared and algorithm-specific logic is separated.

```text
data/
    OR-Library benchmark files

src/
    problem.py
    data_loader.py
    representation.py
    feasibility.py
    repair.py
    objectives.py
    operators.py
    dominance.py
    nsga2.py
    spea2.py
    metrics.py
    statistics.py
    plotting.py
    validation.py

experiments/
    config.py
    seeds.py
    run_single.py
    run_pilot.py
    run_experiments.py

tests/
    unit and integration tests

results/
    raw/
    summary/
    figures/

docs/
    WORKFLOW.md
    PSEUDOCODE.md
    REPORT_OUTLINE.md
    WEEKLY_PROGRESS.md
```

---

# 4. Phase 1 — Prepare the Benchmark Data

The project uses the required OR-Library Capacitated Warehouse Location benchmark instances.

Required instances:

| Category | Instances | Facilities | Customers |
|---|---|---:|---:|
| Small | `cap41`, `cap42` | 16 | 50 |
| Medium | `cap101`, `cap102` | 25 | 50 |
| Large | `cap121`, `cap122` | 50 | 50 |

Workflow:

```text
Download official OR-Library files
        ↓
Store them in data/
        ↓
Parse each file
        ↓
Validate number of facilities/customers
        ↓
Validate capacities, fixed costs, demands and allocation costs
        ↓
Confirm total capacity can cover total demand
```

Commands:

```bash
python -m src.download_data
python scripts/verify_data.py
```

Important project rule:

```text
Use OR-Library allocation costs directly.
Do not multiply allocation cost by customer demand again.
```

---

# 5. Phase 2 — Define the Common CFLP Representation

The baseline uses one gene per customer.

```text
[a0, a1, a2, ..., an-1]
```

where:

```text
aj = facility assigned to customer j
```

Example:

```text
[3, 1, 1, 5, 3]
```

Interpretation:

```text
Customer 0 -> Facility 3
Customer 1 -> Facility 1
Customer 2 -> Facility 1
Customer 3 -> Facility 5
Customer 4 -> Facility 3
```

A facility is considered open if at least one customer is assigned to it.

This representation is shared by both MOEAs.

---

# 6. Phase 3 — Generate Feasible Initial Solutions

The initializer attempts to create feasible solutions from the beginning.

Workflow:

```text
Take all customers
        ↓
Prioritize higher-demand customers
        ↓
Track remaining facility capacities
        ↓
Assign each customer only to facilities with sufficient capacity
        ↓
Check final feasibility
        ↓
Repeat if necessary
```

The same initialization method is used by NSGA-II and SPEA2.

---

# 7. Phase 4 — Feasibility Checking and Repair

Every candidate solution must satisfy:

```text
1. Every customer is assigned exactly once.
2. Every assigned facility is treated as open.
3. No facility exceeds its capacity.
```

Because there is one gene per customer, the first condition is inherent in the representation.

Because every used facility is treated as open, the second condition is also inherent.

The main explicit constraint is capacity.

Workflow:

```text
Candidate chromosome
        ↓
Calculate facility loads
        ↓
Any overload?
   ┌────┴────┐
   │         │
  No        Yes
   │         │
Evaluate   Repair
             ↓
       Move customers from
       overloaded facilities
             ↓
       If direct repair fails
             ↓
       Rebuild feasible assignment
```

Repair is shared by both MOEAs.

---

# 8. Phase 5 — Evaluate the Two Objectives

Only feasible solutions are evaluated.

## Objective 1 — Facility-opening cost

\[
f_1=\sum_i F_i y_i
\]

where \(F_i\) is the fixed opening cost of facility \(i\).

## Objective 2 — Customer-allocation cost

\[
f_2=\sum_i\sum_j C_{ij}x_{ij}
\]

where \(C_{ij}\) is the OR-Library allocation cost.

Workflow:

```text
Feasible chromosome
        ↓
Identify used/open facilities
        ↓
Sum fixed opening costs -> f1
        ↓
Sum customer allocation costs -> f2
        ↓
Return objective vector (f1, f2)
```

---

# 9. Phase 6 — Shared Variation Operators

Both algorithms use the same crossover and mutation operators.

Current baseline:

```text
Crossover:
    Uniform crossover

Mutation:
    Reassign one randomly selected customer to another facility
```

After crossover or mutation:

```text
offspring
    ↓
repair
    ↓
feasibility check
    ↓
objective evaluation
```

This keeps the comparison fair.

---

# 10. Phase 7 — Run NSGA-II

NSGA-II uses:

```text
Non-dominated sorting
        ↓
Front ranks
        ↓
Crowding distance
        ↓
Binary tournament selection
        ↓
Shared crossover + mutation
        ↓
Parents + offspring
        ↓
Elitist environmental selection
```

Selection rule:

```text
Lower front rank is preferred.
If ranks are equal, larger crowding distance is preferred.
```

NSGA-II does not use an external archive.

---

# 11. Phase 8 — Run SPEA2

SPEA2 uses:

```text
Population + archive
        ↓
Strength calculation
        ↓
Raw fitness
        ↓
Density estimation
        ↓
Combined SPEA2 fitness
        ↓
External archive
        ↓
Environmental selection
        ↓
Truncation when archive is too large
        ↓
Tournament selection
        ↓
Shared crossover + mutation
```

Selection rule:

```text
Lower SPEA2 fitness is preferred.
```

SPEA2 maintains an explicit external archive.

---

# 12. Phase 9 — Fair Experimental Design

The algorithms must be compared under the same conditions.

For every seed:

```text
Generate one common initial population
        ↓
        COPY
       /    \
 NSGA-II    SPEA2
```

Within the same configuration, both algorithms use the same:

```text
population size
initialization
representation
repair
crossover
mutation
crossover probability
mutation probability
objective-evaluation budget
benchmark instance
random seed
```

Only their MOEA-specific selection and survivor mechanisms differ.

---

# 13. Phase 10 — Parameter Configurations

Current baseline configurations:

| Configuration | Population | Crossover | Mutation | Max objective evaluations |
|---|---:|---:|---:|---:|
| C1 | 40 | 0.80 | 0.10 | 12,000 |
| C2 | 60 | 0.80 | 0.10 | 12,000 |
| C3 | 60 | 0.80 | 0.20 | 12,000 |

Interpretation:

```text
C1 -> C2:
effect of increasing population size

C2 -> C3:
effect of increasing mutation probability
```

These values should be confirmed after the pilot experiment before final reporting.

---

# 14. Phase 11 — Pilot Experiment

Before the full experiment matrix, run a small pilot.

Recommended pilot:

```text
Instance: cap41
Configuration: C1
A few seeds
Algorithms: NSGA-II and SPEA2
```

Verify:

```text
- all final solutions are feasible;
- objective values are sensible;
- evaluation counts are correct;
- runtimes are practical;
- result CSV files are produced;
- Hypervolume calculation works;
- Pareto plots are generated;
- both algorithms use the same budget.
```

Command:

```bash
python experiments/run_pilot.py
```

---

# 15. Phase 12 — Full Experiment Matrix

Default detailed comparison:

```text
Instances:
    cap41
    cap101
    cap121

Configurations:
    C1
    C2
    C3

Seeds:
    42, 43, 44, 45, 46,
    47, 48, 49, 50, 51

Algorithms:
    NSGA-II
    SPEA2
```

Total main runs:

\[
3 \times 3 \times 10 \times 2 = 180
\]

Command:

```bash
python experiments/run_experiments.py
```

For every run, save:

```text
algorithm
instance
configuration
seed
Hypervolume
number of non-dominated solutions
execution time
objective evaluations
final approximation set
```

---

# 16. Phase 13 — Hypervolume

Hypervolume must use the same scaling and the same reference point for both algorithms on the same benchmark instance.

Workflow:

```text
Collect approximation sets from
both algorithms, all configurations,
and all seeds for one instance
        ↓
Find common min/max for f1 and f2
        ↓
Normalize all objective values
with the same bounds
        ↓
Use common reference point
        ↓
Calculate Hypervolume
```

Normalization:

\[
f_k^{norm}=
\frac{f_k-f_k^{min}}
     {f_k^{max}-f_k^{min}}
\]

Current normalized reference point:

\[
(1.1,1.1)
\]

for the minimization problem.

---

# 17. Phase 14 — Statistical Analysis

For every instance/configuration pair:

```text
10 NSGA-II HV values
        +
10 SPEA2 HV values
        ↓
Pair by random seed
        ↓
Calculate:
    mean HV
    standard deviation HV
    best HV
    worst HV
    mean non-dominated count
    mean execution time
        ↓
Paired Wilcoxon signed-rank test
```

Expected outputs:

```text
results/raw/experiment_runs.csv
results/summary/summary.csv
results/summary/wilcoxon_hv.csv
results/summary/hv_normalization.json
```

---

# 18. Phase 15 — Pareto-Front Plots

For report figures, compare the algorithms under the same:

```text
instance
configuration
seed
```

Axes:

```text
x-axis = f1 facility-opening cost
y-axis = f2 customer-allocation cost
```

Planned report plots:

```text
cap41_report_pareto.png
cap101_report_pareto.png
cap121_report_pareto.png
```

Each plot shows both algorithms on the same axes.

---

# 19. Phase 16 — Final Analysis

The final analysis should discuss:

```text
Convergence:
    Are approximation sets moving toward better objective values?

Diversity:
    How well are solutions spread across the trade-off front?

Hypervolume:
    Which configurations produce better combined convergence and coverage?

Non-dominated count:
    How many distinct trade-off solutions are returned?

Runtime:
    What computational cost is associated with each algorithm/configuration?

Parameter effects:
    What changes when population size or mutation probability changes?
```

---

# 20. Final Deliverable Flow

```text
Verified implementation
        ↓
Pilot completed
        ↓
Parameters frozen
        ↓
Full experiments completed
        ↓
Results summarized
        ↓
Pareto plots produced
        ↓
Statistical comparison completed
        ↓
Report written from actual results
        ↓
Fresh-clone reproducibility test
        ↓
Final GitHub repository
        ↓
PDF report submission
```

---

# 21. Related Documentation

```text
docs/WORKFLOW.md
    -> overall project and experimental flow

docs/PSEUDOCODE.md
    -> detailed algorithm logic

DESIGN_DECISIONS.md
    -> why specific design choices were made

EXPERIMENT_PLAN.md
    -> exact experiment settings and matrix

docs/REPORT_OUTLINE.md
    -> final report structure

docs/WEEKLY_PROGRESS.md
    -> progress documentation
```
