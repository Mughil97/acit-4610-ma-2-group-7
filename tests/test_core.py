import random

from app.algorithms import create_algorithm
from app.algorithms.nsga2 import crowding_distances, non_dominated_sort
from app.config import CONFIGS
from app.problem.loader import load_by_name
from app.problem.repair import decode, repair_binary
from app.problem.representation import random_binary
from app.utils.pareto import dominates, non_dominated


def test_pareto_dominance_minimization():
    assert dominates((1, 2), (1, 3))
    assert not dominates((1, 3), (1, 2))
    assert non_dominated([(1, 3), (2, 2), (3, 1), (2, 4)]) == [(1, 3), (2, 2), (3, 1)]


def test_loader_dimensions_cap61():
    instance = load_by_name("cap61")
    assert instance.m == 16
    assert instance.n == 50
    assert len(instance.alloc_cost) == instance.m
    assert all(len(row) == instance.n for row in instance.alloc_cost)


def test_binary_repair_produces_feasible_assignment():
    instance = load_by_name("cap121")
    rng = random.Random(42)
    individual = repair_binary(random_binary(instance, rng), instance, rng)
    assignment = decode(individual, instance)
    assert all(facility is not None for facility in assignment)
    loads = [0.0] * instance.m
    for customer, facility in enumerate(assignment):
        assert individual[facility] == 1
        loads[facility] += instance.demand[customer]
    assert all(loads[i] <= instance.capacity[i] for i in range(instance.m))


def test_both_algorithms_start_from_same_binary_population_for_same_seed():
    instance = load_by_name("cap61")
    config = CONFIGS[0]
    vega = create_algorithm("vega", instance, config, 42, "binary")
    nsga = create_algorithm("nsga2", instance, config, 42, "binary")
    p1 = [vega.new_individual() for _ in range(config.pop_size)]
    p2 = [nsga.new_individual() for _ in range(config.pop_size)]
    assert p1 == p2


def test_non_dominated_sort_and_crowding():
    objectives = [(1, 4), (2, 3), (3, 2), (4, 1), (3, 4)]
    fronts, ranks = non_dominated_sort(objectives)
    assert set(fronts[0]) == {0, 1, 2, 3}
    assert ranks[4] > 1
    distances = crowding_distances(objectives, fronts)
    assert distances[0] == float("inf")
    assert distances[3] == float("inf")


def test_requested_evaluation_budget_is_respected():
    instance = load_by_name("cap61")
    config = CONFIGS[0]
    for name in ("vega", "nsga2"):
        algorithm = create_algorithm(name, instance, config, 42, "binary")
        algorithm.run()
        assert algorithm.evaluations == config.max_evaluations
