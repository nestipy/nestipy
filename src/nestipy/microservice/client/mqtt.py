import asyncio
from typing import Any, AsyncIterator

from aiomqtt import Client

from .base import ClientProxy, MicroserviceOption


class MqttClientProxy(ClientProxy):
    client: Client

    def __init__(
        self,
        option: MicroserviceOption,
    ):
        super().__init__(option)
        self.client = Client(
            self.option.option.host,
            port=self.option.option.port,
            max_queued_incoming_messages=10,
            max_queued_outgoing_messages=10,
        )

    async def slave(self) -> "ClientProxy":
        return MqttClientProxy(
            option=self.option,
        )

    async def connect(self):
        await self.client.__aenter__()

    async def _publish(self, topic, data):
        await self.client.publish(topic, data, retain=False)

    async def subscribe(self, *args, **kwargs):
        await self.client.subscribe(*args, **kwargs)
        pass

    async def unsubscribe(self, *args):
        await self.client.unsubscribe(*args)
        pass

    async def send_response(self, topic, data):
        await self._publish(topic, data)

    async def listen(self) -> AsyncIterator[str]:
        async for message in self.client.messages:
            yield message.payload.decode("utf-8")
        await asyncio.sleep(0.01)

    async def listen_response(self, from_topic: str, timeout: int = 30) -> Any:
        async for message in self.client.messages:
            return message.payload.decode("utf-8")
        await asyncio.sleep(0.01)

    async def close(self):
        await self.client.__aexit__(None, None, None)
