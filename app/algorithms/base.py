"""The generational loop shared by both MOEAs; a subclass only chooses parents and survivors."""

import random

from app.algorithms.operators import crossover, mutate
from app.problem.evaluation import evaluate
from app.problem.repair import repair
from app.problem.representation import random_individual
from app.utils.pareto import non_dominated


class MOEA:
    name = "MOEA"

    def __init__(self, instance, config, seed):
        self.instance = instance
        self.config = config
        self.rng = random.Random(seed)  # one generator for everything, so a seed repeats a run
        self.evaluations = 0
        self.history = []  # objectives of every generation
        self.on_generation = None  # optional function(generation number, objectives), e.g. a live plot

    def run(self):
        """Evolve until the evaluation budget is used; return the final non-dominated (f1, f2) points."""
        population = [self.new_individual() for _ in range(self.config.pop_size)]
        objectives = self.evaluate_all(population)
        self.record(objectives)

        while self.evaluations < self.config.max_evaluations:
            mating_pool = self.select_parents(population, objectives)
            offspring = self.reproduce(mating_pool)
            offspring_objectives = self.evaluate_all(offspring)
            population, objectives = self.environmental_selection(
                population, objectives, offspring, offspring_objectives
            )
            self.record(objectives)

        return non_dominated(objectives)

    def record(self, objectives):
        self.history.append(objectives)
        if self.on_generation:
            self.on_generation(len(self.history) - 1, objectives)

    def new_individual(self):
        return repair(random_individual(self.instance, self.rng), self.instance, self.rng)

    def reproduce(self, mating_pool):
        """Pair consecutive parents: crossover, mutation, repair."""
        children = []
        for k in range(0, len(mating_pool), 2):
            child1, child2 = crossover(mating_pool[k], mating_pool[k + 1], self.config.crossover_prob, self.rng)
            for child in (child1, child2):
                child = mutate(child, self.config.mutation_prob, self.rng)
                children.append(repair(child, self.instance, self.rng))
        return children

    def evaluate_all(self, population):
        self.evaluations += len(population)
        return [evaluate(individual, self.instance) for individual in population]

    def select_parents(self, population, objectives):
        """Return the mating pool: pop_size individuals."""
        raise NotImplementedError

    def environmental_selection(self, population, objectives, offspring, offspring_objectives):
        """Return (next_population, next_objectives)."""
        raise NotImplementedError
