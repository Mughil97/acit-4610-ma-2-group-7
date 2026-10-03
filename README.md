# ACIT4610 Project 2  - Group 7

# Multi-Objective Evolutionary Optimization for the Capacitated Facility Location Problem (CFLP)

## Project Overview

This project investigates the application and comparison of multi-objective evolutionary algorithms (MOEAs) for solving the Capacitated Facility Location Problem (CFLP).

The CFLP is a combinatorial optimization problem where the goal is to decide which facilities should be opened and how customers should be assigned to facilities while satisfying capacity constraints.

The problem involves conflicting objectives:

1. Minimizing facility opening costs
2. Minimizing customer allocation costs

Because improving one objective may negatively affect another, the solution is not a single optimal point but a set of trade-off solutions represented by the Pareto front.

This project implements and compares two evolutionary optimization approaches:

- VEGA (Vector Evaluated Genetic Algorithm)
- NSGA-II (Non-dominated Sorting Genetic Algorithm II)

The algorithms are evaluated using benchmark CFLP instances from the OR-Library.

## Problem Description

The Capacitated Facility Location Problem consists of:

- A set of candidate facilities
- A set of customers
- Facility opening costs
- Facility capacity constraints
- Customer demands
- Customer-to-facility allocation costs

A feasible solution must satisfy:

- Every customer is assigned to exactly one facility
- Customers are only assigned to available facilities
- Facility capacity limitations are respected

The challenge is balancing the two conflicting objectives:

### Objective 1: Facility Opening Cost

Minimize:

\[
f_1 = \sum_i F_i y_i
\]

where:

- \(F_i\) is the fixed opening cost of facility \(i\)
- \(y_i\) indicates whether facility \(i\) is opened

### Objective 2: Customer Allocation Cost

Minimize:

\[
f_2 = \sum_i\sum_j C_{ij}x_{ij}
\]

where:

- \(C_{ij}\) represents the cost of assigning customer \(j\) to facility \(i\)
- \(x_{ij}\) indicates whether customer \(j\) is assigned to facility \(i\)

Both objectives are minimized simultaneously.

## Algorithms

### VEGA (Vector Evaluated Genetic Algorithm)

VEGA is a multi-objective evolutionary algorithm that separates selection according to individual objectives.

The population is divided according to objectives, where each subgroup is evaluated using one objective before recombination and mutation.

Workflow:

Population initialization\
→ Objective evaluation\
→ Objective-based selection\
→ Crossover\
→ Mutation\
→ Replacement\
→ Repeat

### NSGA-II (Non-dominated Sorting Genetic Algorithm II)

NSGA-II is a Pareto-based evolutionary algorithm designed to maintain both convergence and diversity.

It uses:

- Non-dominated sorting
- Crowding distance
- Elitist environmental selection

Workflow:

Population initialization\
→ Objective evaluation\
→ Non-dominated sorting\
→ Crowding distance\
→ Selection\
→ Crossover\
→ Mutation\
→ Elitist replacement\
→ Repeat

Both algorithms are implemented under the same experimental framework to allow a fair comparison.

## Solution Representation

The project uses a chromosome-based representation for evolutionary optimization.

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

### Binary Chromosome Representation

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

The chromosome represents only facility opening decisions. Customer-to-facility assignments are generated during the decoding step.

### Repair and Decoding

Evolutionary operators such as crossover and mutation may create infeasible solutions.
Therefore, a repair procedure is applied before objective evaluation.

The repair and decoding process ensures that:

- the selected facilities provide sufficient capacity to satisfy total customer demand;
- each customer is assigned to a feasible open facility;
- facility capacity constraints are respected.

The decoding process transforms the binary chromosome into a complete CFLP solution:

```text
Binary Chromosome
        ↓
Identify Open Facilities
        ↓
Assign Customers to Feasible Facilities
        ↓
Generate Complete Solution
        ↓
Evaluate Objectives
```

After decoding, the solution can be evaluated using the two objective functions:

1. Facility opening cost
2. Customer allocation cost

The same chromosome representation, repair mechanism, and objective evaluation procedure are used by both VEGA 
and NSGA-II to ensure a fair algorithm comparison.

## Dataset

The project uses benchmark Capacitated Facility Location Problem instances from the OR-Library.

The evaluated instances are:

- cap61
- cap62
- cap101
- cap102
- cap121
- cap122

Each instance contains:

- Number of facilities
- Number of customers
- Facility capacities
- Facility opening costs
- Customer demands
- Customer-facility allocation costs

## Experimental Setup

The algorithms are evaluated using multiple configurations with different evaluation budgets.

### Configurations

| Configuration | Maximum Evaluations |
| --- | ---: |
| C1 | 10,000 |
| C2 | 20,000 |
| C3 | 40,000 |

Each configuration is evaluated using multiple independent runs to account for the stochastic nature of evolutionary algorithms.

**The experiments are performed on small, medium, and large CFLP benchmark instances to analyse algorithm behavior under different problem scales.**

## Evaluation Metrics

Algorithms are compared using:

- Hypervolume (HV)
- Number of non-dominated solutions
- Execution time
- Pareto-front visualization

### Hypervolume (HV)

Hypervolume measures the quality of the obtained Pareto front by considering both convergence and diversity.

A higher hypervolume indicates that the obtained solutions dominate a larger portion of the objective space relative to a reference point.

## Repository Structure

```text
ACIT4610_Project2/

│
├── app/
│   │
│   ├── algorithms/
│   │   ├── vega.py
│   │   ├── nsga2.py
│   │   └── operators.py
│   │
│   ├── problem/
│   │   ├── loader.py
│   │   ├── representation.py
│   │   ├── repair.py
│   │   └── evaluation.py
│   │
│   └── utils/
│       └── pareto.py
│
├── data/
│   └── CFLP benchmark instances
│
├── tests/
│
├── results/
│
├── run_experiments.py
│
├── requirements.txt
│
└── README.md
```

## Installation

### 1. Clone the repository

Clone the GitHub repository:

```bash
git clone https://github.com/Mughil97/acit-4610-ma-2-group-7.git
```

Navigate to the project folder:

```bash
cd acit-4610-ma-2-group-7
```

### 2. Create and activate a virtual environment (recommended)

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

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Running Tests

Run the test suite using:

```bash
pytest
```

The tests verify important project components, including:

- Pareto dominance calculations
- Problem instance loading
- Solution representation and handling
- Algorithm components

A successful test run confirms that the core components are working correctly before running experiments.

## Running Experiments

Run the complete experiment setup:

```bash
python run_experiments.py
```

The generated results include:

- Objective values (`f1`, `f2`)
- Non-dominated solutions
- Pareto front data
- Hypervolume measurements
- Runtime statistics
- Pareto front visualizations

## AI Use Disclosure

During the development of this project, generative AI tools, including ChatGPT (OpenAI) and Claude (Anthropic), were used as supporting tools for permitted coding-related activities.

The tools were used for:

Technical and coding clarification: Clarifying programming concepts, algorithm behaviour, and implementation requirements.

Project scaffolding: The project's file structure and code scaffolding using factory pattern.

Data visualisation: Assisting with Python/Matplotlib code used to generate plots and visualise experimental results.

Code review and refactoring: Assisting with debugging and refactoring code for better performance, readability, and structure.

All algorithmic decisions, parameter choices, experiments, outputs, and final code were reviewed and verified by the group.

The final written report was produced by the group members in their own words in accordance with the assignment's AI-use requirements.
