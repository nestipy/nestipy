import pytest

from nestipy.ioc.dependency import TypeAnnotated
from nestipy.metadata import Reflect
from nestipy.microservice.context import RpcRequest, RpcResponse
from nestipy.microservice.decorator import (
    MessagePattern,
    EventPattern,
    MICROSERVICE_LISTENER,
    MicroserviceMetadata,
)
from nestipy.microservice.dependency import Client, Payload, Ctx, Context
from nestipy.microservice.serializer import JSONSerializer
from nestipy.microservice.client.option import Transport, TCPClientOption


@pytest.mark.asyncio
async def test_json_serializer_roundtrip():
    serializer = JSONSerializer()
    data = {"a": 1}
    payload = await serializer.serialize(data)
    assert isinstance(payload, str)
    restored = await serializer.deserialize(payload)
    assert restored == data


def test_rpc_request_is_event():
    req = RpcRequest(data={"x": 1}, pattern="ping")
    assert req.is_event() is True
    req2 = RpcRequest(data={"x": 1}, pattern="ping", response_topic="resp")
    assert req2.is_event() is False
    resp = RpcResponse(pattern="ping", data={"ok": True}, status="success")
    assert resp.pattern == "ping"


def test_microservice_decorators_set_metadata():
    def handler():
        return None

    decorated = MessagePattern("ping")(handler)
    meta = Reflect.get_metadata(decorated, MICROSERVICE_LISTENER, None)
    assert meta is not None
    assert meta.pattern == "ping"
    assert meta.type == MicroserviceMetadata.Message

    decorated = EventPattern("pong")(handler)
    meta = Reflect.get_metadata(decorated, MICROSERVICE_LISTENER, None)
    assert meta is not None
    assert meta.pattern == "pong"
    assert meta.type == MicroserviceMetadata.Event


def test_microservice_dependency_aliases():
    dep = Client("token")
    assert isinstance(dep, TypeAnnotated)
    assert Payload is not None
    assert Ctx is not None
    assert Context is RpcRequest


def test_microservice_options_defaults():
    opt = TCPClientOption()
    assert opt.host == "localhost"
    assert opt.port == 1333
    assert Transport.TCP.value == "TCP"
