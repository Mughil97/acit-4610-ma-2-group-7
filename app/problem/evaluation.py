"""Objective evaluation (both minimised), computed only on feasible solutions.

f1 = sum_i F_i * y_i          facility-opening cost

f2 = sum_i sum_j C_ij * x_ij  customer-allocation cost

The OR-Library allocation costs already include demand.
"""

import numpy as np

from app.problem.loader import CFLPInstance


def evaluate(
    open_mask: np.ndarray,
    assignment: np.ndarray,
    instance: CFLPInstance,
) -> tuple[float, float]:
    """
    Return (f1, f2) for a feasible solution.

    Parameters
    ----------
    open_mask:
        Binary vector indicating opened facilities.
        Example:
        [1,0,1,0]

    assignment:
        Facility assigned to each customer.
        Example:
        [2,0,2,1]

    instance:
        CFLP problem instance.

    Returns
    -------
    tuple:
        (facility opening cost, allocation cost)
    """

    # Objective 1:
    # Sum fixed costs of opened facilities
    f1 = np.sum(
        instance.fixed_cost[open_mask == 1]
    )

    # Objective 2:
    # Sum customer-to-facility allocation costs
    f2 = 0.0

    for customer, facility in enumerate(assignment):
        f2 += instance.alloc_cost[customer, facility]

    return float(f1), float(f2)
