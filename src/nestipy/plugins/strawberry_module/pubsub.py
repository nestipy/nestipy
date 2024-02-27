import asyncio
from typing import Any

from pyee import EventEmitter

STRAWBERRY_PUB_SUB = "STRAWBERRY_PUB_SUB"


class PubSub:
    def __init__(self):
        self.ee = EventEmitter()

    async def asyncIterator(self, event: str):
        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def handler(value):
            loop.call_soon_threadsafe(future.set_result, value)

        self.ee.on(event, handler)
        try:
            while True:
                yield await future
                future = loop.create_future()  # Reset the future for the next value
        finally:
            self.ee.remove_listener(event, handler)

    def publish(self, event: str, data: Any):
        self.ee.emit(event, data)
