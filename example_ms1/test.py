import asyncio
import logging


async def awaited():
    await asyncio.sleep(1)


async def task1():
    while True:
        logging.info("Task 1 running...")
        await awaited()  # Non-blocking operation to yield control


async def task2():
    while True:
        logging.info("Task 2 running...")
        await asyncio.sleep(2)  # Non-blocking operation to yield control


async def main():
    logging.info("Starting tasks...")

    # Get the current event loop
    loop = asyncio.get_running_loop()

    # Schedule tasks to run indefinitely
    task1_handle = loop.create_task(task1())
    task2_handle = loop.create_task(task2())

    try:
        # Optionally, await for other conditions or events
        await asyncio.sleep(10)  # Run the tasks for 10 seconds for demonstration

    finally:
        # Cancel tasks if needed (optional)
        task1_handle.cancel()
        task2_handle.cancel()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
