import asyncio

import pytest

from nestipy.websocket.adapter.socketio import SocketIoAdapter


class FakeAsyncServer:
    def __init__(self):
        self.handlers = {}
        self.emitted = []
        self.handled = False
        self._environ = {
            "asgi.scope": {"type": "websocket", "path": "/socket.io"},
            "asgi.receive": lambda: None,
            "asgi.send": lambda _: None,
        }

    def on(self, event, namespace=None):
        def decorator(fn):
            self.handlers[(event, namespace)] = fn
            return fn

        return decorator

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
            (event, data, to, room, skip_sid, namespace, callback, ignore_queue)
        )

    async def handle_request(self, scope, receive, send):
        self.handled = True

    def get_environ(self, sid, namespace):
        return self._environ


def test_socketio_adapter_on_event():
    fake = FakeAsyncServer()
    adapter = SocketIoAdapter(fake)
    called = {}

    @adapter.on("ping")
    async def handler(event, client, data):
        called["event"] = event
        called["data"] = data
        called["sid"] = client.sid
        return "ok"

    wrapper = fake.handlers[("ping", None)]
    asyncio.run(wrapper("sid-1", {"x": 1}))

    assert called["event"] == "ping"
    assert called["data"] == {"x": 1}
    assert called["sid"] == "sid-1"


def test_socketio_adapter_connect_disconnect():
    fake = FakeAsyncServer()
    adapter = SocketIoAdapter(fake)
    called = {"connect": False, "disconnect": False}

    @adapter.on_connect()
    async def on_connect(sid, client, data):
        called["connect"] = True

    @adapter.on_disconnect()
    async def on_disconnect(sid, client, data):
        called["disconnect"] = True

    connect_handler = fake.handlers[("connect", None)]
    disconnect_handler = fake.handlers[("disconnect", None)]

    asyncio.run(connect_handler("sid-1", fake.get_environ("sid-1", None)))
    assert "sid-1" in adapter._connected

    asyncio.run(disconnect_handler("sid-1"))
    assert "sid-1" not in adapter._connected
    assert called["connect"] is True
    assert called["disconnect"] is True


@pytest.mark.asyncio
async def test_socketio_adapter_call_delegates_to_server():
    fake = FakeAsyncServer()
    adapter = SocketIoAdapter(fake)

    scope = {"type": "http", "path": "/socket.io"}

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(_):
        return None

    result = await adapter(scope, receive, send)
    assert result is True
    assert fake.handled is True
