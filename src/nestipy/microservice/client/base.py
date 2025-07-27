import asyncio
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict
from dataclasses import field, dataclass
from typing import AsyncIterator, Any, Union
from typing import Optional

from nestipy.microservice.context import RpcRequest, RpcResponse, MICROSERVICE_CHANNEL
from nestipy.microservice.exception import RpcException, RPCErrorMessage, RPCErrorCode
from nestipy.microservice.serializer import Serializer, JSONSerializer
from .option import RabbitMQClientOption, TCPClientOption, GrpcClientOption
from .option import RedisClientOption, MqttClientOption, NatsClientOption
from .option import Transport


@dataclass
class MicroserviceOption:
    transport: Transport = field(default=Transport.TCP)
    option: Optional[
        Union[
            RedisClientOption,
            MqttClientOption,
            NatsClientOption,
            RabbitMQClientOption,
            TCPClientOption,
            GrpcClientOption,
        ]
    ] = None
    proxy: Optional["ClientProxy"] = None
    serializer: Serializer = field(default=JSONSerializer())
    channel_key: str = field(default="nestipy")
    timeout: int = 30

    def __post_init__(self):
        if (
            self.transport == Transport.TCP
            and self.option is not None
            and not isinstance(self.option, TCPClientOption)
        ):
            raise ValueError("Option must be of type TCPClientOption for TCP transport")
        elif (
            self.transport == Transport.REDIS
            and self.option is not None
            and not isinstance(self.option, RedisClientOption)
        ):
            raise ValueError(
                "Option must be of type RedisClientOption for REDIS transport"
            )
        elif (
            self.transport == Transport.MQTT
            and self.option is not None
            and not isinstance(self.option, MqttClientOption)
        ):
            raise ValueError(
                "Option must be of type MqttClientOption for MQTT transport"
            )
        elif (
            self.transport == Transport.NATS
            and self.option is not None
            and not isinstance(self.option, NatsClientOption)
        ):
            raise ValueError(
                "Option must be of type NatsClientOptions for NATS transport"
            )
        elif (
            self.transport == Transport.RABBITMQ
            and self.option is not None
            and not isinstance(self.option, RabbitMQClientOption)
        ):
            raise ValueError(
                "Option must be of type RabbitMQClientOption for RABBITMQ transport"
            )

        elif (
            self.transport == Transport.GRPC
            and self.option is not None
            and not isinstance(self.option, GrpcClientOption)
        ):
            raise ValueError(
                "Option must be of type GrpcClientOption for GRPC transport"
            )


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

    async def before_start(self):
        await asyncio.sleep(0.001)

    async def before_close(self):
        await asyncio.sleep(0.001)

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
        response_channel = f"{MICROSERVICE_CHANNEL}:response:{request.response_topic}"
        await self.subscribe(response_channel)
        await self._publish(
            f"{MICROSERVICE_CHANNEL}:{self.option.channel_key}",
            await self.option.serializer.serialize(asdict(request)),
        )
        #  add timeout
        try:
            async with asyncio.timeout(self.option.timeout):
                rpc_response = await self.listen_response(
                    response_channel, self.option.timeout
                )
        except asyncio.TimeoutError:
            raise RpcException(
                status_code=RPCErrorCode.DEADLINE_EXCEEDED,
                message=RPCErrorMessage.DEADLINE_EXCEEDED,
            )
        await self.unsubscribe(response_channel)
        await self.close()
        json_rep = await self.option.serializer.deserialize(rpc_response)
        response = RpcResponse.from_dict(json_rep)
        if response.exception:
            raise response.exception
        return response

    async def emit(self, topic, data, headers: dict[str, str] = None):
        request = RpcRequest(pattern=topic, data=data, headers=headers or {})
        json_req = await self.option.serializer.serialize(asdict(request))
        await self._publish(
            f"{MICROSERVICE_CHANNEL}:{self.option.channel_key}", json_req
        )

    @abstractmethod
    def listen(self) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        pass

    @abstractmethod
    async def close(self):
        pass
