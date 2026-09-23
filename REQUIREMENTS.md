# Assignment Requirements Checklist

This checklist maps the project brief to concrete repository tasks.

## Problem and objectives

- [ ] Solve the multi-objective CFLP.
- [ ] Minimize fixed facility-opening cost `f1`.
- [ ] Minimize customer-allocation cost `f2`.
- [ ] Keep the two objectives separate.
- [ ] Return a non-dominated approximation set rather than one weighted-sum solution.
- [ ] Do not multiply `C_ij` by customer demand again.

## Feasibility

Every evaluated solution must satisfy:

- [ ] every customer assigned exactly once;
- [ ] assignment only to an opened facility;
- [ ] no facility exceeds capacity;
- [ ] objectives calculated only after feasibility is established.

## Data

Use the original OR-Library values for:

- [ ] fixed opening cost `F_i`;
- [ ] facility capacity `S_i`;
- [ ] customer demand `d_j`;
- [ ] allocation cost `C_ij`.

Required files:

- [ ] `cap41`
- [ ] `cap42`
- [ ] `cap101`
- [ ] `cap102`
- [ ] `cap121`
- [ ] `cap122`

## Shared problem-specific design

Both MOEAs must use the same:

- [ ] representation;
- [ ] initialization;
- [ ] feasibility/repair logic;
- [ ] crossover;
- [ ] mutation;
- [ ] objective functions.

## NSGA-II

- [ ] Pareto dominance.
- [ ] Non-dominated sorting.
- [ ] Crowding distance.
- [ ] Binary tournament selection.
- [ ] Crossover and mutation.
- [ ] Elitist environmental selection using parents + offspring.

## SPEA2

- [ ] Strength calculation.
- [ ] Raw fitness.
- [ ] Density estimation.
- [ ] External archive.
- [ ] Environmental selection.
- [ ] Distance-based archive truncation.
- [ ] Tournament selection.
- [ ] Crossover and mutation.

## Experimental fairness

Within each configuration, both algorithms use the same:

- [ ] population size;
- [ ] initialization method;
- [ ] crossover probability;
- [ ] mutation probability;
- [ ] termination/evaluation budget;
- [ ] random seed set;
- [ ] benchmark instance.

## Required experiment design

- [ ] Three parameter configurations.
- [ ] At least 10 independent runs per algorithm/instance/configuration.
- [ ] Fixed/reported random seeds.
- [ ] One selected small instance.
- [ ] One selected medium instance.
- [ ] One selected large instance.
- [ ] Code can load all six required instances.

## Metrics

For every reported algorithm/instance/configuration combination:

- [ ] Hypervolume.
- [ ] Number of non-dominated solutions.
- [ ] Execution time.
- [ ] Final approximation set.

For Hypervolume:

- [ ] same normalization for both algorithms on an instance;
- [ ] same reference point for both algorithms;
- [ ] reference point worse than all comparison solutions;
- [ ] exact procedure documented.

## Summary statistics

- [ ] Mean HV.
- [ ] Standard deviation HV.
- [ ] Best HV.
- [ ] Worst HV.
- [ ] Mean number of non-dominated solutions.
- [ ] Mean execution time.

## Plots

- [ ] Small-instance Pareto comparison.
- [ ] Medium-instance Pareto comparison.
- [ ] Large-instance Pareto comparison.
- [ ] Both algorithms shown on the same axes.
- [ ] Plot comparisons use the same configuration and seed for both algorithms.

## Repository and reproducibility

- [ ] Clean Python code.
- [ ] Core evolutionary logic implemented explicitly.
- [ ] Data loading separated.
- [ ] Representation separated.
- [ ] Feasibility/repair separated.
- [ ] Objective evaluation separated.
- [ ] Metrics separated.
- [ ] Statistics separated.
- [ ] Plotting separated.
- [ ] Executable experiment scripts.
- [ ] Installation instructions.
- [ ] Dependency list.
- [ ] Fixed seeds.
- [ ] Fresh-clone test completed.

## Report

- [ ] PDF submission.
- [ ] 1000–1500 words.
- [ ] Group number included.
- [ ] Real-world CFLP description and mathematical definition.
- [ ] Example encoded individual and repair/decoding explanation.
- [ ] Exact OR-Library data fields described.
- [ ] Complete MOEA implementation described.
- [ ] Differences in MOEA selection/environmental replacement explained.
- [ ] Common experimental budget/settings reported.
- [ ] Required statistics table(s) included.
- [ ] Three Pareto-front plots included.
- [ ] Effects of the three configurations analyzed.
- [ ] GitHub link included and tested.
