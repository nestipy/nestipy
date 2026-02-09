import asyncio

import pytest

from nestipy.common import Module
from nestipy.ioc import NestipyContainer
from nestipy.metadata import Reflect, ModuleMetadata
from nestipy.websocket.proxy import IoSocketProxy
from nestipy.websocket.decorator import Gateway, SubscribeMessage, SuccessEvent


class FakeIoAdapter:
    def __init__(self):
        self.handlers = {}
        self.emitted = []

    def _register(self, event, namespace=None):
        def decorator(handler):
            self.handlers[(event, namespace)] = handler
            return handler

        return decorator

    def on_message(self):
        return self._register("__WS_MESSAGE_SUBSCRIBE__")

    def on_connect(self):
        return self._register("__WS_ON_CONNECT__")

    def on_disconnect(self):
        return self._register("__WS_ON_DISCONNECT__")

    def on(self, event, namespace=None):
        return self._register(event, namespace)

    async def emit(
        self,
        event,
        data=None,
        to=None,
        room=None,
        skip_sid=None,
        namespace=None,
        callback=None,
        ignore_queue=False,
    ):
        self.emitted.append(
            {
                "event": event,
                "data": data,
                "to": to,
                "namespace": namespace,
            }
        )


class FakeHttpAdapter:
    def __init__(self, io_adapter):
        self._io_adapter = io_adapter

    def get_io_adapter(self):
        return self._io_adapter


@Gateway("/")
@SuccessEvent("pong")
class ChatGateway:
    @SubscribeMessage("ping")
    async def handle(self):
        return "ok"


@Module(providers=[ChatGateway])
class AppModule:
    pass


@pytest.mark.asyncio
async def test_io_socket_proxy_registers_and_emits():
    NestipyContainer.clear()
    io_adapter = FakeIoAdapter()
    http_adapter = FakeHttpAdapter(io_adapter)
    proxy = IoSocketProxy(http_adapter)

    proxy.apply_routes([AppModule])

    handler = io_adapter.handlers.get(("ping", "/"))
    assert handler is not None

    class Client:
        sid = "sid-1"

    await handler("ping", Client(), {"x": 1})

    assert io_adapter.emitted
    assert io_adapter.emitted[0]["event"] == "pong"
    assert io_adapter.emitted[0]["to"] == "sid-1"
