import asyncio
from typing import AsyncIterator

import nats
from nats.aio.client import Client
from nats.aio.subscription import Subscription

from .base import ClientProxy, MicroserviceOption

NATS_QUEUE = "microservice:queue"


class NatsClientProxy(ClientProxy):
    client: Client
    consumer: Subscription

    def __init__(self, option: MicroserviceOption):
        super().__init__(option)

    async def slave(self) -> "ClientProxy":
        return NatsClientProxy(
            self.option,
        )

    async def connect(self):
        self.client = await nats.connect(self.option.url)

    async def _publish(self, topic: str, data: str):
        await self.client.publish(topic, data.encode())

    async def subscribe(self, *args, **kwargs):
        self.consumer = await self.client.subscribe(*args, **kwargs, queue=NATS_QUEUE)

    async def unsubscribe(self, *args):
        await self.consumer.unsubscribe()

    async def send_response(self, topic: str, data: str):
        await self._publish(topic, data)

    async def listen(self) -> AsyncIterator[str]:
        while True:
            async for msg in self.consumer.messages:
                yield msg.data.decode("utf-8")
            await asyncio.sleep(0.01)

    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        while True:
            async for msg in self.consumer.messages:
                return msg.data.decode("utf-8")
            await asyncio.sleep(0.01)

    async def close(self):
        await self.client.close()
