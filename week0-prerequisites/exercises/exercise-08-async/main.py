import asyncio

async def async_function():
    print("Start of async function")
    await asyncio.sleep(3)
    print("End of async function")


async def task_two():
    print("Start of task two")
    await asyncio.sleep(1)
    print("End of task two")

async def main():
    await asyncio.gather(
        async_function(),
        task_two()
    )


asyncio.run(main())