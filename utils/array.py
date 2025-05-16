import random
from typing import List, TypeVar

T = TypeVar('T')

def weighted_random_choice(choices: List[T], weights: List[float]) -> T:
    total_weight = sum(weights)
    random_weight = random.random() * total_weight

    cumulative_weight = 0
    for choice, weight in zip(choices, weights):
        cumulative_weight += weight
        if random_weight <= cumulative_weight:
            return choice

    # Fallback in case of rounding errors
    return choices[-1]
