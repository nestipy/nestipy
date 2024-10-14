import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict
from dataclasses import field, dataclass
from typing import AsyncIterator, Any
from typing import Optional

import async_timeout

from nestipy.microservice.context import RpcRequest, RpcResponse, MICROSERVICE_CHANNEL
from nestipy.microservice.exception import RpcException, RPCErrorMessage, RPCErrorCode
from nestipy.microservice.serilaizer import Serializer, JSONSerializer
from .option import Transport, MicroserviceClientOption


@dataclass
class MicroserviceOption:
    transport: Transport = field(default=Transport.REDIS)
    option: Optional[MicroserviceClientOption] = None
    url: Optional[str] = None
    proxy: Optional["ClientProxy"] = None
    serializer: Serializer = field(default=JSONSerializer())
    timeout: int = 30


class ClientProxy(ABC):
    def __init__(self, option: MicroserviceOption):
        self.option = option

    @abstractmethod
    async def slave(self) -> "ClientProxy":
        pass

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def _publish(self, topic, data):
        pass

    @abstractmethod
    async def subscribe(self, *args, **kwargs):
        pass

    @abstractmethod
    async def unsubscribe(self, *args):
        pass

    @abstractmethod
    async def send_response(self, topic, data):
        pass

    async def send(
        self, topic, data: Any, headers: dict[str, str] = None
    ) -> RpcResponse:
        await self.connect()
        response_topic = uuid.uuid4().hex
        request = RpcRequest(
            pattern=topic,
            data=data,
            response_topic=response_topic,
            headers=headers or {},
        )
        await self.subscribe(response_topic)
        await self._publish(
            MICROSERVICE_CHANNEL,
            await self.option.serializer.serialize(asdict(request)),
        )
        #  add timeout
        try:
            with async_timeout.timeout(self.option.timeout):
                rpc_response = await self.listen_response(
                    response_topic, self.option.timeout
                )
        except asyncio.TimeoutError:
            raise RpcException(
                status_code=RPCErrorCode.DEADLINE_EXCEEDED,
                message=RPCErrorMessage.DEADLINE_EXCEEDED,
            )
        await self.unsubscribe(response_topic)
        await self.close()
        json_rep = await self.option.serializer.deserialize(rpc_response)
        response = RpcResponse.from_dict(json_rep)
        if response.exception:
            raise response.exception
        return response

    async def emit(self, topic, data, headers: dict[str, str] = None):
        request = RpcRequest(pattern=topic, data=data, headers=headers or {})
        json_req = await self.option.serializer.serialize(asdict(request))
        await self._publish(topic, json_req)

    @abstractmethod
    def listen(self) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        pass

    @abstractmethod
    async def close(self):
        pass
