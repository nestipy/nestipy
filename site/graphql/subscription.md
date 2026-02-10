Subscriptions stream events over WebSocket. Use `@Subscription()` to return an async iterator.

## Basic Subscription

```python
import asyncio
from typing import AsyncIterator, Annotated

from nestipy.graphql import Resolver
from nestipy.graphql.decorator import Subscription
from nestipy.ioc import Arg


@Resolver()
class EventsResolver:
    @Subscription()
    async def ticks(self, count: Annotated[int, Arg()] = 5) -> AsyncIterator[int]:
        for i in range(count):
            yield i
            await asyncio.sleep(0.5)
```

## PubSub Helper

Nestipy includes a simple PubSub helper for subscriptions:

```python
from typing import AsyncIterator
from nestipy.graphql import Resolver, PubSub
from nestipy.graphql.decorator import Subscription


pubsub = PubSub()


@Resolver()
class EventsResolver:
    @Subscription()
    async def events(self) -> AsyncIterator[str]:
        async for value in pubsub.async_iterator("events"):
            yield value


# Somewhere else in your code
pubsub.publish("events", "hello")
```

## Tips

- Use PubSub for simple in-process eventing.
- For production, consider a distributed pub/sub system if you scale horizontally.
