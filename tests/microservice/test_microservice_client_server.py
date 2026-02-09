import asyncio
from dataclasses import asdict

import pytest

from nestipy.microservice.client.base import ClientProxy, MicroserviceOption
from nestipy.microservice.client.factory import ClientModuleFactory
from nestipy.microservice.client.module import ClientsConfig, ClientsModule
from nestipy.microservice.client.option import (
    Transport,
    TCPClientOption,
    RedisClientOption,
)
from nestipy.microservice.context import RpcRequest, RpcResponse, MICROSERVICE_CHANNEL
from nestipy.microservice.exception import RpcException, RPCErrorCode
from nestipy.microservice.server.base import MicroServiceServer


class FakeClientProxy(ClientProxy):
    def __init__(self, option: MicroserviceOption):
        super().__init__(option)
        self.published = []
        self.subscribed = []
        self.unsubscribed = []
        self.connected = False
        self.closed = False
        self.listen_payloads = []
        self.slave_instance = None

    async def slave(self) -> "FakeClientProxy":
        self.slave_instance = FakeClientProxy(self.option)
        return self.slave_instance

    async def connect(self):
        self.connected = True

    async def _publish(self, topic, data):
        self.published.append((topic, data))

    async def subscribe(self, *args, **_kwargs):
        self.subscribed.append(args[0] if args else None)

    async def unsubscribe(self, *args):
        self.unsubscribed.append(args[0] if args else None)

    async def send_response(self, topic, data):
        self.published.append((topic, data))

    async def listen(self):
        for payload in list(self.listen_payloads):
            yield payload

    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        response = RpcResponse(pattern=from_topic, data={"ok": True}, status="success")
        return await self.option.serializer.serialize(asdict(response))

    async def close(self):
        self.closed = True


class TimeoutClientProxy(FakeClientProxy):
    async def listen_response(self, from_topic: str, timeout: int = 30) -> str:
        raise asyncio.TimeoutError


def test_microservice_option_validation():
    with pytest.raises(ValueError):
        MicroserviceOption(transport=Transport.TCP, option=RedisClientOption())
    with pytest.raises(ValueError):
        MicroserviceOption(transport=Transport.REDIS, option=TCPClientOption())


def test_client_module_factory_custom_proxy():
    proxy = FakeClientProxy(MicroserviceOption(transport=Transport.CUSTOM))
    option = MicroserviceOption(transport=Transport.CUSTOM, proxy=proxy)
    created = ClientModuleFactory.create(option)
    assert created is proxy


def test_client_module_factory_defaults_tcp():
    option = MicroserviceOption(transport=Transport.TCP, option=None)
    created = ClientModuleFactory.create(option)
    assert created.__class__.__name__ == "TCPClientProxy"
    assert isinstance(option.option, TCPClientOption)


def test_client_module_factory_custom_requires_proxy():
    option = MicroserviceOption(transport=Transport.CUSTOM, proxy=None)
    with pytest.raises(Exception):
        ClientModuleFactory.create(option)


def test_clients_module_register_builds_providers():
    proxy = FakeClientProxy(MicroserviceOption(transport=Transport.CUSTOM))
    option = MicroserviceOption(transport=Transport.CUSTOM, proxy=proxy)
    config = ClientsConfig(name="svc", option=option)
    dynamic_module = ClientsModule.register([config])

    tokens = [provider.token for provider in dynamic_module.providers]
    assert "svc" in tokens
    assert dynamic_module.is_global is True


@pytest.mark.asyncio
async def test_client_proxy_send_and_emit():
    option = MicroserviceOption(transport=Transport.CUSTOM)
    client = FakeClientProxy(option)

    response = await client.send("ping", {"hello": "world"})
    assert response.data == {"ok": True}
    assert client.connected is True
    assert client.closed is True
    assert client.subscribed
    assert client.unsubscribed

    topic, payload = client.published[0]
    assert topic == f"{MICROSERVICE_CHANNEL}:{option.channel_key}"
    req_data = await option.serializer.deserialize(payload)
    assert req_data["pattern"] == "ping"
    assert req_data["response_topic"] is not None

    await client.emit("event", {"x": 1})
    topic, payload = client.published[-1]
    assert topic == f"{MICROSERVICE_CHANNEL}:{option.channel_key}"
    req_data = await option.serializer.deserialize(payload)
    assert req_data["pattern"] == "event"
    assert req_data["response_topic"] is None


@pytest.mark.asyncio
async def test_client_proxy_send_timeout():
    option = MicroserviceOption(transport=Transport.CUSTOM)
    client = TimeoutClientProxy(option)

    with pytest.raises(RpcException) as exc:
        await client.send("ping", {"hello": "world"})

    assert exc.value.status_code == RPCErrorCode.DEADLINE_EXCEEDED


@pytest.mark.asyncio
async def test_microservice_server_handle_request_success():
    option = MicroserviceOption(transport=Transport.CUSTOM)
    client = FakeClientProxy(option)
    server = MicroServiceServer(client)

    async def handler(_server, _request):
        return {"ok": True}

    server.request_subscribe("ping", handler)

    request = RpcRequest(data={"id": 1}, pattern="ping", response_topic="resp-1")
    await server.handle_request(request)

    slave = client.slave_instance
    assert slave is not None
    topic, payload = slave.published[0]
    assert topic == f"{MICROSERVICE_CHANNEL}:response:{request.response_topic}"
    data = await option.serializer.deserialize(payload)
    assert data["status"] == "success"


@pytest.mark.asyncio
async def test_microservice_server_handle_request_not_found():
    option = MicroserviceOption(transport=Transport.CUSTOM)
    client = FakeClientProxy(option)
    server = MicroServiceServer(client)

    request = RpcRequest(data={"id": 1}, pattern="missing", response_topic="resp-2")
    await server.handle_request(request)

    slave = client.slave_instance
    assert slave is not None
    assert slave.closed is True
    topic, payload = slave.published[0]
    assert topic == f"{MICROSERVICE_CHANNEL}:response:{request.response_topic}"
    data = await option.serializer.deserialize(payload)
    assert data["status"] == "error"
    assert data["exception"]["status_code"] == RPCErrorCode.NOT_FOUND


@pytest.mark.asyncio
async def test_microservice_server_listen_event():
    option = MicroserviceOption(transport=Transport.CUSTOM)
    client = FakeClientProxy(option)
    server = MicroServiceServer(client)
    called = {"value": False}

    async def handler(_server, _request):
        called["value"] = True

    server.subscribe("event", handler)

    request = RpcRequest(data={"x": 1}, pattern="event")
    payload = await option.serializer.serialize(asdict(request))
    client.listen_payloads = [payload]

    await server.listen()

    assert called["value"] is True
    assert client.subscribed == [f"{MICROSERVICE_CHANNEL}:{option.channel_key}"]
