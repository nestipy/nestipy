import asyncio
from typing import AsyncIterator, Union, cast

import async_timeout
from aio_pika import connect_robust, Message, ExchangeType
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from aio_pika.abc import AbstractRobustQueue, AbstractRobustExchange

from .base import ClientProxy, MicroserviceOption


class RabbitMQClientProxy(ClientProxy):
    connection: AbstractRobustConnection
    channel: AbstractRobustChannel
    exchange: AbstractRobustExchange
    consumer_queue: Union[AbstractRobustQueue, None]
    CHANGE = "microservice:exchange"

    def __init__(self, option: MicroserviceOption):
        super().__init__(option)

    async def slave(self) -> "ClientProxy":
        return RabbitMQClientProxy(
            self.option,
        )

    async def connect(self):
        self.connection = await connect_robust(
            host=self.option.option.host, port=self.option.option.port
        )
        self.channel = await self.connection.channel()
        await self.channel.__aenter__()
        self.exchange = await self.channel.declare_exchange(
            self.CHANGE, ExchangeType.FANOUT
        )

    async def _publish(self, topic: str, data: str):
        await self.exchange.publish(Message(body=data.encode()), routing_key=topic)

    async def send_response(self, topic: str, data: str):
        response_exchange = await self.channel.declare_exchange(
            f"{self.CHANGE}:{topic}", ExchangeType.FANOUT
        )
        await response_exchange.publish(Message(body=data.encode()), routing_key=topic)

    async def subscribe(self, *args, **kwargs):
        self.consumer_queue = await self.channel.declare_queue(*args)
        await self.consumer_queue.bind(self.exchange)

    async def unsubscribe(self, *args):
        await self.consumer_queue.unbind(self.exchange)
        await self.consumer_queue.delete()

    async def listen(self) -> AsyncIterator[str]:
        if self.consumer_queue is not None:
            async with self.consumer_queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        msg = cast(Message, message)
                        yield msg.body.decode("utf-8")

    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        response_exchange = await self.channel.declare_exchange(
            f"{self.CHANGE}:{from_topic}", ExchangeType.FANOUT
        )
        response_queue = await self.channel.declare_queue(from_topic)
        await response_queue.bind(response_exchange)
        try:
            with async_timeout.timeout(timeout):
                async with response_queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            msg = cast(Message, message)
                            if message.routing_key == from_topic:
                                res = msg.body.decode("utf-8")
                                break

        except asyncio.TimeoutError as e:
            raise e
        finally:
            await response_queue.unbind(response_exchange)
            await response_queue.delete()
            await response_exchange.delete()
        return res

    async def close(self):
        await self.channel.__aexit__(None, None, None)
        await self.connection.close()
