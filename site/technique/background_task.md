You can define background tasks to be run without waiting.

```python
import asyncio
from typing import Annotated

from nestipy.common import Injectable
from nestipy.core import BackgroundTasks
from nestipy.ioc import Inject


async def long_task1():
    print("Task 1")
    await asyncio.sleep(2)
    print("Task1 finished")


async def long_task2():
    print("Task 2")
    await asyncio.sleep(2)
    print("Task2 finished")


@Injectable()
class AppService:
    tasks: Annotated[BackgroundTasks, Inject()]

    def start(self):
        self.tasks.add_task(long_task1)
        self.tasks.add_task(long_task2)
        print("Task registered")
```

### Background Tasks and Asyncio Queue

Using `self.tasks.add_task`, the function is added to an **asyncio Queue**. If the queue is empty, the function is executed immediately.

The `BackgroundTasks` feature can be utilized in scenarios such as:

- Sending emails without blocking the response.
- Performing long-running processes asynchronously, ensuring the user receives a response without delays.

This approach improves performance and responsiveness by offloading time-consuming tasks to the background.

