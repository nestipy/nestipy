import asyncio
import typing
from dataclasses import asdict
from typing import AsyncIterator

from redis.asyncio import Redis, client

from .base import ClientProxy, MicroserviceOption
from .option import RedisClientOption


class RedisClientProxy(ClientProxy):
    broker: Redis
    pub_sub: client.PubSub

    def __init__(self, option: MicroserviceOption):
        super().__init__(option)

    async def connect(self):
        option = typing.cast(
            RedisClientOption, self.option.option or RedisClientOption()
        )
        # url = f"redis://{option.host}:{option.port}"
        # self.broker = Redis.from_url(url, max_connections=10, decode_responses=True)
        self.broker = Redis(**asdict(option))
        self.pub_sub = self.broker.pubsub()
        await self.pub_sub.connect()

    async def _publish(self, topic, data):
        await self.broker.publish(topic, data)

    async def send_response(self, topic, data):
        await self._publish(topic, data)

    async def listen(self) -> AsyncIterator[str]:
        while True:
            message = await self.pub_sub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                if message["type"] == "message":
                    yield message["data"]
            await asyncio.sleep(0.01)

    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        async for message in self.pub_sub.listen():
            if message is not None:
                if message["type"] == "message":
                    response = message["data"]
                    return response

    async def close(self):
        await self.pub_sub.aclose()
        await self.broker.close()

    async def subscribe(self, *args, **kwargs):
        await self.pub_sub.subscribe(*args, **kwargs)

    async def unsubscribe(self, *args):
        await self.pub_sub.unsubscribe(*args)

    async def slave(self) -> "ClientProxy":
        return RedisClientProxy(self.option)
