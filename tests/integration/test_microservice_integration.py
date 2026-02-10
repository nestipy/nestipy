from dataclasses import asdict
from typing import Annotated

import pytest

from nestipy.common import Controller, Injectable, Module
from nestipy.ioc import Inject, NestipyContainer
from nestipy.ioc.context_container import RequestContextContainer
from nestipy.microservice.client.base import ClientProxy, MicroserviceOption
from nestipy.microservice.client.option import Transport
from nestipy.microservice.context import RpcRequest, RpcResponse, MICROSERVICE_CHANNEL
from nestipy.microservice.decorator import MessagePattern, EventPattern
from nestipy.microservice.dependency import Payload, Headers, Pattern, Ctx
from nestipy.microservice.exception import RpcException, RPCErrorCode, RPCErrorMessage
from nestipy.core import NestipyMicroservice


class InMemoryClientProxy(ClientProxy):
    def __init__(self, option: MicroserviceOption):
        super().__init__(option)
        self.published: list[tuple[str, str]] = []
        self.subscribed: list[str] = []
        self.unsubscribed: list[str] = []
        self.listen_payloads: list[str] = []
        self.slave_instance: InMemoryClientProxy | None = None
        self.connected = False
        self.closed = False

    async def slave(self) -> "InMemoryClientProxy":
        self.slave_instance = InMemoryClientProxy(self.option)
        return self.slave_instance

    async def _connect(self):
        self.connected = True
        self._mark_connected()

    async def _publish(self, topic, data):
        self.published.append((topic, data))

    async def subscribe(self, *args, **_kwargs):
        if args:
            self.subscribed.append(args[0])

    async def unsubscribe(self, *args):
        if args:
            self.unsubscribed.append(args[0])

    async def send_response(self, topic, data):
        self.published.append((topic, data))

    async def listen(self):
        for payload in list(self.listen_payloads):
            yield payload

    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        response = RpcResponse(pattern=from_topic, data={"ok": True}, status="success")
        return await self.option.serializer.serialize(asdict(response))

    async def _close(self):
        self.closed = True
        self._mark_disconnected()


@pytest.mark.asyncio
async def test_microservice_integration_message_and_event_flow():
    NestipyContainer.clear()
    RequestContextContainer.get_instance().destroy()

    @Injectable()
    class MathService:
        def add(self, a: int, b: int) -> int:
            return a + b

    @Controller()
    class MathController:
        service: Annotated[MathService, Inject()]
        last_event_pattern: str | None = None

        @MessagePattern("sum")
        async def sum(
            self,
            payload: Annotated[dict, Payload()],
            pattern: Annotated[str, Pattern()],
            headers: Annotated[dict, Headers()],
        ):
            return {
                "sum": self.service.add(payload["a"], payload["b"]),
                "pattern": pattern,
                "trace": headers.get("x-trace"),
            }

        @EventPattern("touch")
        async def touch(self, ctx: Annotated[object, Ctx()]):
            type(self).last_event_pattern = ctx.get_pattern()

    @Module(controllers=[MathController], providers=[MathService])
    class AppModule:
        pass

    option = MicroserviceOption(transport=Transport.CUSTOM)
    client = InMemoryClientProxy(option)
    option.proxy = client

    microservice = NestipyMicroservice(AppModule, [option])

    try:
        await microservice.ms_setup()
        server = microservice.servers[0]

        request = RpcRequest(
            data={"a": 2, "b": 3},
            pattern="sum",
            response_topic="resp-1",
            headers={"x-trace": "abc"},
        )
        await server.handle_request(request)

        slave = client.slave_instance
        assert slave is not None
        topic, payload = slave.published[0]
        assert topic == f"{MICROSERVICE_CHANNEL}:response:{request.response_topic}"

        response_data = await option.serializer.deserialize(payload)
        assert response_data["status"] == "success"
        assert response_data["data"] == {
            "sum": 5,
            "pattern": "sum",
            "trace": "abc",
        }

        event_request = RpcRequest(data={"ping": True}, pattern="touch")
        client.listen_payloads = [
            await option.serializer.serialize(asdict(event_request))
        ]
        await server.listen()
        assert MathController.last_event_pattern == "touch"
    finally:
        await microservice.stop()
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()


@pytest.mark.asyncio
async def test_microservice_integration_error_and_context_injection():
    NestipyContainer.clear()
    RequestContextContainer.get_instance().destroy()

    @Injectable()
    class ErrorService:
        def fail(self) -> None:
            raise ValueError("boom")

    @Controller()
    class ErrorController:
        service: Annotated[ErrorService, Inject()]

        @MessagePattern("fail-rpc")
        async def fail_rpc(self, ctx: Annotated[object, Ctx()]):
            assert ctx.get_pattern() == "fail-rpc"
            raise RpcException(
                status_code=RPCErrorCode.INVALID_ARGUMENT,
                message="bad input",
            )

        @MessagePattern("fail-generic")
        async def fail_generic(self, headers: Annotated[dict, Headers()]):
            assert headers.get("x-test") == "1"
            self.service.fail()
            return {"ok": True}

    @Module(controllers=[ErrorController], providers=[ErrorService])
    class AppModule:
        pass

    option = MicroserviceOption(transport=Transport.CUSTOM)
    client = InMemoryClientProxy(option)
    option.proxy = client

    microservice = NestipyMicroservice(AppModule, [option])

    try:
        await microservice.ms_setup()
        server = microservice.servers[0]

        request_rpc = RpcRequest(
            data={"id": 1}, pattern="fail-rpc", response_topic="resp-rpc"
        )
        await server.handle_request(request_rpc)

        slave_rpc = client.slave_instance
        assert slave_rpc is not None
        _, payload_rpc = slave_rpc.published[0]
        response_rpc = await option.serializer.deserialize(payload_rpc)
        assert response_rpc["status"] == "error"
        assert response_rpc["exception"]["status_code"] == RPCErrorCode.INVALID_ARGUMENT
        assert response_rpc["exception"]["message"] == "bad input"

        request_generic = RpcRequest(
            data={"ok": True},
            pattern="fail-generic",
            response_topic="resp-generic",
            headers={"x-test": "1"},
        )
        await server.handle_request(request_generic)

        slave_generic = client.slave_instance
        assert slave_generic is not None
        _, payload_generic = slave_generic.published[0]
        response_generic = await option.serializer.deserialize(payload_generic)
        assert response_generic["status"] == "error"
        assert response_generic["exception"]["status_code"] == RPCErrorCode.INTERNAL
        assert RPCErrorMessage.INTERNAL in response_generic["exception"]["message"]
    finally:
        await microservice.stop()
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()
