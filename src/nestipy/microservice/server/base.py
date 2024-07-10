from abc import ABC
from dataclasses import asdict
from typing import Callable, Any

from nestipy.microservice.client import ClientProxy
from nestipy.microservice.client.option import Transport
from nestipy.microservice.context import RpcRequest, RpcResponse, MICROSERVICE_CHANNEL
from nestipy.microservice.exception import RpcException, RPCErrorCode, RPCErrorMessage
from nestipy.microservice.serilaizer import Serializer


class MicroServiceServer(ABC):
    def __init__(self, pubsub: ClientProxy, serializer: Serializer):
        self._pubsub = pubsub
        self._serializer = serializer
        self._subscriptions: list[tuple[str, Callable]] = []
        self._request_subscriptions: list[tuple[str, Callable]] = []

    async def listen(self):
        await self._pubsub.connect()
        await self._pubsub.subscribe(MICROSERVICE_CHANNEL)
        async for data in self._pubsub.listen():
            print("OnData ::", data)
            json_rep = await self._serializer.deserialize(data)
            request = RpcRequest(**json_rep)
            if request.is_event():
                await self.handle_event(request)
            else:
                await self.handle_request(request=request)

    def get_transport(self) -> Transport:
        return self._pubsub.option.transport

    async def close(self):
        await self._pubsub.close()

    def subscribe(self, topic: str, callback: Callable):
        self._subscriptions.append((topic, callback))

    def unsubscribe(self, topic: str):
        for sub in self._subscriptions:
            if sub[0] == topic:
                self._subscriptions.remove(sub)

    def request_subscribe(self, topic: str, callback: Callable):
        self._request_subscriptions.append((topic, callback))

    def request_unsubscribe(self, topic: str):
        for sub in self._request_subscriptions:
            if sub[0] == topic:
                self._request_subscriptions.remove(sub)

    async def handle_request(self, request: RpcRequest) -> Any:
        # process pattern
        slave = await self._pubsub.slave()
        await slave.connect()
        for (pattern, callback) in self._request_subscriptions:
            if pattern == request.pattern:
                # resolve dependencies
                response = await callback(self, request)
                rpc_response = RpcResponse(
                    pattern=request.response_topic,
                    data=response,
                    status="success"
                )
                await slave.send_response(
                    request.response_topic,
                    await self._serializer.serialize(asdict(rpc_response))
                )
                return
        rpc_response = await self._serializer.serialize(
            asdict(
                RpcResponse(
                    pattern=request.pattern,
                    data=None,
                    status="error",
                    exception=RpcException(
                        status_code=RPCErrorCode.NOT_FOUND,
                        message=RPCErrorMessage.NOT_FOUND
                    )
                )
            )
        )
        await slave.send_response(
            request.response_topic,
            rpc_response
        )
        await slave.close()

    async def handle_event(self, request: RpcRequest):
        # process pattern
        for (pattern, callback) in self._subscriptions:
            if pattern == request.pattern:
                await callback(self, request)
