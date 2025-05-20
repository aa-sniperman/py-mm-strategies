import random
from typing import List

def random_array_with_sum(length: int, total_sum: float, min_val: float, max_val: float) -> List[float]:
    remaining = total_sum
    results = []
    
    for _ in range(length - 1):
        rand = random.uniform(min_val, max_val)
        amount = min(remaining, rand)
        remaining -= amount
        results.append(amount)
    
    results.append(remaining)
    return results
