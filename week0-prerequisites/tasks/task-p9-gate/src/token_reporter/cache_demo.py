from functools import lru_cache
from time import sleep
from time import perf_counter

@lru_cache
def expensive_operation(text: str):

    sleep(2)

    return len(text)

start = perf_counter()

print(
    expensive_operation(
        "Hello World"
    )
)

end = perf_counter()


print(
    f"Execution Time: {end-start:.2f}"
)

start = perf_counter()

print(
    expensive_operation(
        "Hello World"
    )
)

end = perf_counter()

print(
    f"Execution Time: {end-start:.2f}"
)