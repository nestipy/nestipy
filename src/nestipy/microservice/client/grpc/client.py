import asyncio
import typing
from typing import AsyncIterator

import grpc

import nestipy.microservice.client.grpc.microservice_pb2 as pb2
import nestipy.microservice.client.grpc.microservice_pb2_grpc as pb2_grpc
from nestipy.microservice.client.base import ClientProxy, MicroserviceOption
from nestipy.microservice.client.option import GrpcClientOption
from nestipy.microservice.exception import RpcException, RPCErrorCode, RPCErrorMessage
from .server import GrpcServer


class GrpcClientProxy(ClientProxy):
    def __init__(self, option: MicroserviceOption):
        super().__init__(option)
        self.channel: typing.Optional[grpc.Channel] = None
        self.stub: typing.Optional[pb2_grpc.GrpcStub] = None
        self.subscription: typing.Optional[AsyncIterator[pb2.DataResponse]] = None
        self.response_queue = asyncio.Queue()
        self._config = typing.cast(
            GrpcClientOption, self.option.option or GrpcClientOption()
        )
        self.loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        self.server: GrpcServer = GrpcServer()
        self.server_task: typing.Optional[asyncio.Task] = None

    async def slave(self) -> "ClientProxy":
        """Clone the client proxy."""
        return GrpcClientProxy(self.option)

    async def before_start(self):
        self.server_task = self.loop.create_task(
            coro=self.server.serve(port=self._config.port), name="grpc_server"
        )

    async def before_close(self):
        if self.server_task:
            self.server_task.cancel()

    async def connect(self):
        """Establish a connection to the gRPC server."""
        if not self.channel:
            self.channel = grpc.aio.insecure_channel(
                f"{self._config.host}:{self._config.port}"
            )
            self.stub = pb2_grpc.GrpcStub(self.channel)

    async def _publish(self, topic, data):
        """Publish data"""
        request = pb2.DataRequest(topic=topic, data=data)
        await self.stub.SendData(request)

    async def send_response(self, topic, data):
        """Send a response message."""
        await self._publish(topic, data)

    async def subscribe(self, topic: str, *args, **kwargs):
        sub_request = pb2.SubRequest(topic=topic)
        self.subscription = self.stub.Subscribe(sub_request)

    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        """Listen for a response using an async queue."""
        try:
            async with asyncio.timeout(timeout):
                async for response in self.subscription:
                    if response.topic == from_topic:
                        return response.data
        except asyncio.TimeoutError:
            raise RpcException(
                status_code=RPCErrorCode.DEADLINE_EXCEEDED,
                message=RPCErrorMessage.DEADLINE_EXCEEDED,
            )

    async def listen(self) -> AsyncIterator[str]:
        """Continuously listen for incoming responses."""
        async for response in self.subscription:
            yield response.data

    async def unsubscribe(self, topic: str, *args):
        """Unsubscribe from topics (not applicable for gRPC)."""
        unsub_request = pb2.UnsubRequest(topic=topic)
        await self.stub.Unsubscribe(unsub_request)

    async def close(self):
        """Close the gRPC channel."""
        if self.channel:
            await self.channel.close()
