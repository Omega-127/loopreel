import asyncio
import random

from race import main

def run(seed: int | None = None) -> tuple[str, ...]:
    if seed is not None:
        random.seed(seed)
    return tuple(asyncio.run(main()))

free = {run() for _ in range(200)}
seed = {run(42) for _ in range(200)}
print("distinct orders, unseeded: ",len(free))
print("distinct orders, seeded: ",len(seed))

from collections import Counter

seeded = Counter(run(42) for _ in range(5000))
for order, count in seeded.most_common():
    print(count, order)
