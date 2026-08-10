import asyncio
from time import perf_counter

async def fetch_news():
    await asyncio.sleep(2)
    return "News Ready"

async def fetch_weather():
    await asyncio.sleep(2)
    return "Weather report ready"

async def main():

    start_time = perf_counter()

    result1, result2 = await asyncio.gather(
        fetch_news(),
        fetch_weather()
    )

   

    print(result1)
    print(result2)
    end_time = perf_counter()

    print(
                f"Execution Time: "
                f"{end_time - start_time:.6f} seconds"
        )

asyncio.run(main())