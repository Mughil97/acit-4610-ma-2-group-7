# Design Decisions

This file records the baseline project decisions and the reason for each one.

## DD-001 — MOEA pair

**Decision:** NSGA-II and SPEA2.

**Reason:** NSGA-II is directly covered by the course lab implementation. The assignment explicitly permits SPEA-2 and lists strength/raw fitness, density estimation, archive, truncation, selection, mutation and variation as its expected core components. The pair also gives a clear comparison between crowding-distance elitist sorting and strength/density archive-based selection.

**Status:** Baseline must be approved.

## DD-002 — Chromosome representation

**Decision:** One integer gene per customer. Gene `j` is the facility serving customer `j`.

Example:

```text
[3, 1, 4, 3, 2]
```

A facility is open when at least one customer is assigned to it.

**Reason:** Every valid chromosome automatically assigns every customer exactly once and makes open-facility consistency explicit. Capacity remains the main feasibility condition that may require repair.

**Status:** Baseline must approved.

## DD-003 — Initialisation

**Decision:** Build feasible individuals directly. Process customers in descending demand order and place each customer in a randomly chosen facility with enough remaining capacity.

**Reason:** The assignment states that objective values must be calculated only after a feasible assignment has been produced. Feasible initialization reduces unnecessary repair at generation 0 while retaining stochastic diversity.

**Status:** Baseline must be approved.

## DD-004 — Repair

**Decision:** Repair overloaded facilities by moving customers to facilities with spare capacity. Prefer moves with small allocation-cost increase. If direct moves become stuck, rebuild a feasible assignment while retaining the current chromosome as a preference.

**Reason:** Uniform crossover and reassignment mutation can violate capacities. Both algorithms must use the same explicit feasibility handling.

**Status:** Baseline must be approved.

## DD-005 — Crossover

**Decision:** Uniform crossover.

**Reason:** The course includes uniform crossover. For a customer-assignment chromosome, every gene is independently meaningful, so uniform inheritance is simple and representation-valid. Capacity is repaired afterward when necessary.

**Status:** Baseline must be approved.

## DD-006 — Mutation

**Decision:** One-customer reassignment mutation.

**Reason:** This is the natural categorical analogue of a local gene mutation: choose one customer and assign it to a different facility, then repair capacity if required.

**Status:** Baseline must be approved.

## DD-007 — Parameter configurations

**Decision:**

| Config | Population | Crossover | Mutation | Max evaluations |
|---|---:|---:|---:|---:|
| C1 | 40 | 0.80 | 0.10 | 12000 |
| C2 | 60 | 0.80 | 0.10 | 12000 |
| C3 | 60 | 0.80 | 0.20 | 12000 |

**Reason:** C1→C2 isolates population-size change. C2→C3 isolates mutation-probability change. The objective-evaluation budget stays fixed.

**Status:** Executable baseline; confirm runtime after pilot before report freeze.

## DD-008 — Objective-evaluation budget

**Decision:** 12000 objective evaluations for each run.

**Reason:** The same objective-evaluation budget is fairer than giving configurations with larger populations the same number of generations.

**Status:** Executable baseline; confirm runtime after pilot.

## DD-009 — Seeds

**Decision:** `42, 43, 44, 45, 46, 47, 48, 49, 50, 51`.

**Reason:** Ten fixed seeds provide the required independent reproducible runs and permit paired algorithm comparisons.

**Status:** Must be approved.

## DD-010 — Detailed benchmark instances

**Decision:** `cap41`, `cap101`, `cap121` by default.

**Reason:** One instance from each required small, medium and large category. All six files remain supported and can be run through the CLI.

**Status:** Baseline must be approved; may be changed before the final experiment batch if documented.

## DD-011 — Hypervolume normalization

**Decision:** For each benchmark instance, use common min-max bounds calculated across final approximation sets from both algorithms, all configurations and all seeds included in the comparison.

**Reason:** Both algorithms are then scored in the same normalized objective space.

**Status:** Baseline must be approved.

## DD-012 — Hypervolume reference point

**Decision:** `(1.1, 1.1)` after common min-max normalization.

**Reason:** All normalized comparison points lie in `[0,1]` for each objective, so the reference point is worse in both minimization objectives.

**Status:** Baseline must be approved.

## DD-013 — Pareto plot selection

**Decision:** Use the same seed for both algorithms. Baseline report plots use seed 42 and configuration C2.

**Reason:** This avoids comparing independently cherry-picked best runs. All configurations also receive paired diagnostic plots.

**Status:** Baseline; the final report may choose another common configuration only if the choice is explicitly justified.
