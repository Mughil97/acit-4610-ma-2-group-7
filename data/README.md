# Data: OR-Library capacitated warehouse location instances

The benchmark instances, from J. E. Beasley's OR-Library. The project uses cap61/62 (small), cap101/102 (medium)
and cap121/122 (large), as set in `app/config.py`. cap41/42 are the small instances the assignment lists, but they
can not be solved under its rules (see below), so the group replaced them with cap61/62.

- Info page: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/capinfo.html
- Files: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/

The files were downloaded on 2026-09-30 and are stored **unmodified**. The assignment forbids
inventing or changing any of these values.

## What the data represents

A company must serve **n customers** from a subset of **m candidate warehouses**.
Each file describes:

- **for every candidate warehouse**: how much demand it can hold (capacity) and what it costs to open (fixed cost);
- **for every customer**: how much it needs (demand), and the cost of serving *all* of that demand
  from each warehouse (allocation cost).

## File format

Values are whitespace separated. A customer's list of `m` costs wraps over several lines.

```
m n                          number of warehouses, number of customers
capacity  fixed_cost         } m lines, one per warehouse
...
demand                       } repeated for each of the n customers:
cost_1 cost_2 ... cost_m     }   demand, then m allocation costs
...
```

## How each field is used

| File field        | Symbol | Used for                                  | `CFLPInstance` attribute      |
|-------------------|--------|-------------------------------------------|-------------------------------|
| fixed cost        | F_i    | Objective 1: facility-opening cost        | `fixed_cost`, shape (m,)      |
| allocation cost   | C_ij   | Objective 2: customer-allocation cost     | `alloc_cost`, shape (m, n)    |
| capacity          | S_i    | Capacity constraint                       | `capacity`, shape (m,)        |
| demand            | d_j    | Capacity constraint                       | `demand`, shape (n,)          |

C_ij is already the cost of the customer's **whole** demand, so Objective 2 must **not** multiply it by d_j.

## Instances

| File         | Category | m  | n  | Capacity per warehouse | Fixed cost per warehouse | Total capacity | Total demand |
|--------------|----------|----|----|------------------------|--------------------------|----------------|--------------|
| `cap41.txt`  | small (not used) | 16 | 50 | 5,000          | 7,500 (one is 0)         | 80,000         | 58,268       |
| `cap42.txt`  | small (not used) | 16 | 50 | 5,000          | 12,500 (one is 0)        | 80,000         | 58,268       |
| `cap61.txt`  | small    | 16 | 50 | 15,000                 | 7,500 (one is 0)         | 240,000        | 58,268       |
| `cap62.txt`  | small    | 16 | 50 | 15,000                 | 12,500 (one is 0)        | 240,000        | 58,268       |
| `cap101.txt` | medium   | 25 | 50 | 58,268                 | 7,500 (one is 0)         | 1,456,700      | 58,268       |
| `cap102.txt` | medium   | 25 | 50 | 58,268                 | 12,500 (one is 0)        | 1,456,700      | 58,268       |
| `cap121.txt` | large    | 50 | 50 | 15,000                 | 7,500 (one is 0)         | 750,000        | 58,268       |
| `cap122.txt` | large    | 50 | 50 | 15,000                 | 12,500 (one is 0)        | 750,000        | 58,268       |

## Properties worth knowing

- **Instance pairs differ only in fixed cost.** Within each pair (41/42, 61/62, 101/102, 121/122) the capacities
  and allocation costs are identical. cap61/62 also have the same allocation costs as cap41/42; only the
  capacity differs (15,000 instead of 5,000).
- **The same 50 customers appear in every file.** Total demand is 58,268 and individual demands range from 31 to 12,912.
- **One warehouse per file is free to open (fixed cost 0).** It is warehouse 11 in cap41/42/61/62/101/102
  (index 10 in the loader) and warehouse 23 in cap121/122 (index 22).
- **Each file has exactly one allocation cost of 0.**
- **In cap101/102 capacity never binds.** Every warehouse can hold the total demand (58,268), so these
  instances are effectively uncapacitated.
- ⚠️ **cap41/42 cannot be solved under single assignment.** Customer 11 (demand 5,495) and customer 34
  (demand 12,912) each need more than any warehouse's capacity of 5,000. The assignment requires every customer
  to be served by exactly one warehouse without exceeding capacity, so no solution satisfies all constraints.
  OR-Library's published optima for these instances allow splitting a customer's demand. The loader still reads
  them, but repair stops with a clear error. cap61/62 hold 15,000 per warehouse, so every customer fits.

## Loading

```python
from app.problem.loader import load_by_name

inst = load_by_name("cap121")   # reads data/cap121.txt
inst.m, inst.n                  # (50, 50)
inst.alloc_cost[i][j]           # cost of serving all of customer j from warehouse i
```

The values are stored as tuples, so any accidental change to OR-Library values raises an error.
