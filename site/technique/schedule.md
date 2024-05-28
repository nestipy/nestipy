Task scheduling allows you to run specific code at set times, regular intervals, or once after a delay. In Linux, tools like cron typically handle this function.
Nestipy offers the `nestipy_schedule` package that utilize the `apscheduler` Python package.

## Installation
```bash
pip install nestipy_schedule
```
We need to register `ScheduleModule` to make it work
```python
from nestipy.common import Module

from app_controller import AppController
from app_service import AppService
from nestipy_schedule import ScheduleModule, ScheduleOption


@Module(
    imports=[
        ScheduleModule.for_root(ScheduleOption())
    ],
    controllers=[AppController],
    providers=[AppService]
)
class AppModule:
    ...
```
We can now use `@Cron`, `@Interaval` or `@Timeout` decorators inside any controller and provider. `ScheduleModule` automatically detects and registers these callbacks..

```python
from typing import Annotated

from nestipy.common import Injectable
from nestipy.ioc import Inject

from nestipy_schedule import Cron, Interval, Timeout, SchedulerRegistry


@Injectable()
class AppService:
    registry: Annotated[SchedulerRegistry, Inject()]

    @classmethod
    async def get(cls):
        return "test"

    @classmethod
    async def post(cls, data: dict):
        return "test"

    @classmethod
    async def put(cls, id_: int, data: dict):
        return "test"

    @classmethod
    async def delete(cls, id_: int):
        return "test"

    @classmethod
    @Cron("0 0 * * *")  # every day at 00:00
    async def cron(cls):
        print("Running every day at 00:00")

    @classmethod
    @Interval(2)
    async def interval(cls):
        print("Running every 2 seconds")

    @classmethod
    @Timeout(5000)
    async def timeout(cls):
        print("Running after 5 seconds")

```
By using `SchedulerRegistry`, we can `add`, `get`, or `remove` a schedule job dynamically.