"""The generational loop shared by both MOEAs; a subclass only chooses parents and survivors."""

import random

from app.algorithms.operators import bit_flip, move_to_open, one_point_crossover, uniform_crossover
from app.problem.evaluation import evaluate_binary, evaluate_integer
from app.problem.repair import repair_binary, repair_integer
from app.problem.representation import random_binary, random_integer
from app.utils.pareto import non_dominated

# representation -> (random start, repair, evaluate, crossover, mutate)
REPRESENTATIONS = {
    "binary": (random_binary, repair_binary, evaluate_binary, uniform_crossover, bit_flip),
    "integer": (random_integer, repair_integer, evaluate_integer, one_point_crossover, move_to_open),
}


class MOEA:
    name = "MOEA"

    def __init__(self, instance, config, seed, representation="binary"):
        self.instance = instance
        self.config = config
        self.rng = random.Random(seed)  # one generator for everything, so a seed repeats a run
        self.evaluations = 0
        self.history = []  # objectives of every generation
        functions = REPRESENTATIONS[representation]
        self.random_individual, self.repair, self.evaluate, self.crossover, self.mutate = functions

    def run(self):
        """Evolve until the evaluation budget is used; return the final non-dominated (f1, f2) points."""
        population = [self.new_individual() for _ in range(self.config.pop_size)]
        objectives = self.evaluate_all(population)
        self.history.append(objectives)

        while self.evaluations < self.config.max_evaluations:
            mating_pool = self.select_parents(population, objectives)
            offspring = self.reproduce(mating_pool)
            offspring_objectives = self.evaluate_all(offspring)
            population, objectives = self.environmental_selection(
                population, objectives, offspring, offspring_objectives
            )
            self.history.append(objectives)

        return non_dominated(objectives)

    def new_individual(self):
        return self.repair(self.random_individual(self.instance, self.rng), self.instance, self.rng)

    def reproduce(self, mating_pool):
        """Pair consecutive parents: crossover, mutation, repair."""
        mutation_prob = self.config.mutation_flips / len(mating_pool[0])  # per gene (facility or customer)
        children = []
        for k in range(0, len(mating_pool), 2):
            child1, child2 = self.crossover(mating_pool[k], mating_pool[k + 1], self.config.crossover_prob, self.rng)
            for child in (child1, child2):
                child = self.mutate(child, mutation_prob, self.rng)
                children.append(self.repair(child, self.instance, self.rng))
        return children

    def evaluate_all(self, population):
        self.evaluations += len(population)
        return [self.evaluate(individual, self.instance) for individual in population]

    def select_parents(self, population, objectives):
        """Return the mating pool: pop_size individuals."""
        raise NotImplementedError

    def environmental_selection(self, population, objectives, offspring, offspring_objectives):
        """Return (next_population, next_objectives)."""
        raise NotImplementedError
