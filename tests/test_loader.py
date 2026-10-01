from pathlib import Path
from app.problem.loader import load_instance

instance = load_instance(
    Path("data/cap61.txt")
)

print(instance.name)
print(instance.m)
print(instance.n)

print(instance.capacity.shape)
print(instance.fixed_cost.shape)
print(instance.demand.shape)
print(instance.alloc_cost.shape)