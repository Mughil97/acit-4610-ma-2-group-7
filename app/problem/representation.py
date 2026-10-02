"""The two ways to store a solution (chosen with --representation; binary by default).

binary:  one 0/1 per facility, individual[i] = 1 means facility i is open (customers are placed by the decoder).
integer: one facility per customer, individual[j] is the facility that serves customer j.
"""


def random_binary(instance, rng):
    return [rng.randrange(2) for _ in range(instance.m)]  # every facility open with probability 0.5


def random_integer(instance, rng):
    return [rng.randrange(instance.m) for _ in range(instance.n)]  # every customer picks a random facility
