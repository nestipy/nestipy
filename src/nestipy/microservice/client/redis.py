import asyncio
from typing import AsyncIterator

from redis.asyncio import Redis, client

from .base import ClientProxy, MicroserviceOption


class RedisClientProxy(ClientProxy):
    broker: Redis
    pubsub: client.PubSub

    def __init__(self, option: MicroserviceOption):
        super().__init__(option)

    async def connect(self):
        url = f"redis://{self.option.option.host}:{self.option.option.port}"
        self.broker = Redis.from_url(url, max_connections=10, decode_responses=True)
        self.pubsub = self.broker.pubsub()
        await self.pubsub.connect()

    async def _publish(self, topic, data):
        await self.broker.publish(topic, data)

    async def send_response(self, topic, data):
        await self._publish(topic, data)

    async def listen(self) -> AsyncIterator[str]:
        while True:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                if message["type"] == "message":
                    yield message["data"]
            await asyncio.sleep(0.01)

    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        async for message in self.pubsub.listen():
            if message is not None:
                if message["type"] == "message":
                    response = message["data"]
                    return response

    async def close(self):
        await self.pubsub.aclose()
        await self.broker.close()

    async def subscribe(self, *args, **kwargs):
        await self.pubsub.subscribe(*args, **kwargs)

    async def unsubscribe(self, *args):
        await self.pubsub.unsubscribe(*args)

    async def slave(self) -> "ClientProxy":
        return RedisClientProxy(self.option)
