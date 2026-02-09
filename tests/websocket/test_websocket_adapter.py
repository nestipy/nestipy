import asyncio

import pytest

from nestipy.websocket.adapter.websocket import WebsocketAdapter
from nestipy.websocket.socket_request import Websocket


@pytest.mark.asyncio
async def test_websocket_adapter_handles_message_and_events():
    events = []
    messages = []
    connects = []
    disconnects = []

    def preprocess(payload, message):
        return "ws", payload

    adapter = WebsocketAdapter(path="/ws", preprocess_payload=preprocess)

    @adapter.on_message()
    async def msg_handler(event, client, data):
        messages.append((event, data))

    @adapter.on_connect()
    async def on_connect(event, client, data):
        connects.append((event, client.sid))

    @adapter.on_disconnect()
    async def on_disconnect(event, client, data):
        disconnects.append((event, client.sid))

    send_messages = []

    async def send(message):
        send_messages.append(message)

    receive_queue = asyncio.Queue()
    await receive_queue.put({"type": "websocket.receive", "text": "hello"})
    await receive_queue.put({"type": "websocket.disconnect"})

    async def receive():
        return await receive_queue.get()

    scope = {"type": "websocket", "path": "/ws"}

    result = await adapter(scope, receive, send)

    assert result is True
    assert any(msg["type"] == "websocket.accept" for msg in send_messages)
    assert messages and messages[0][0] == "ws"
    assert connects
    assert disconnects


@pytest.mark.asyncio
async def test_websocket_adapter_on_wrapper_invokes_handler():
    adapter = WebsocketAdapter(path="/ws")
    called = []

    @adapter.on("ping")
    async def handler(event, client, data):
        called.append((event, data, client.sid))

    async def send(_message):
        return None

    async def receive():
        return {"type": "websocket.disconnect"}

    scope = {"type": "websocket", "path": "/ws"}
    sid = "sid-1"
    client = Websocket(None, sid, None, scope, receive, send)
    adapter._client_info[sid] = client

    wrapper = adapter._event_handlers["ping"]
    await wrapper(sid, "payload")

    assert called == [("ping", "payload", sid)]


@pytest.mark.asyncio
async def test_websocket_adapter_emit():
    adapter = WebsocketAdapter(path="/ws")
    sent = []

    async def send(message):
        sent.append(message)

    async def receive():
        return {"type": "websocket.disconnect"}

    scope = {"type": "websocket", "path": "/ws"}

    sid = "client-1"
    client = Websocket(None, sid, None, scope, receive, send)
    adapter._client_info[sid] = client
    adapter._connected.append(sid)

    await adapter.emit("event", {"a": 1})

    # Expect send calls for websocket.send with bytes payload
    assert any(msg["type"] == "websocket.send" for msg in sent)
    assert any("bytes" in msg for msg in sent)
    assert sid in adapter._client_info
