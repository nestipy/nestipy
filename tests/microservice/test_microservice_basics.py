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
from nestipy.microservice.dependency import Client, Payload, Ctx, Context, Headers, Pattern
from nestipy.ioc.context_container import RequestContextContainer
from nestipy.core.context.execution_context import ExecutionContext
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
    assert Context is not None


@pytest.mark.asyncio
async def test_microservice_dependency_resolution():
    req = RpcRequest(
        data={"foo": "bar"},
        pattern="ping",
        response_topic="resp",
        headers={"x-token": "abc"},
    )
    ctx = ExecutionContext(
        None,
        object(),
        object(),
        lambda: None,
        req,
        None,
        None,
        None,
        None,
        None,
        req.data,
    )
    container = RequestContextContainer.get_instance()
    container.set_execution_context(ctx)
    try:
        payload = Payload().metadata.callback(
            "data", None, dict, container
        )
        assert payload == {"foo": "bar"}

        payload_field = Payload("foo").metadata.callback(
            "data", "foo", str, container
        )
        assert payload_field == "bar"

        headers = Headers().metadata.callback(
            "headers", None, dict, container
        )
        assert headers == {"x-token": "abc"}

        header_one = Headers("x-token").metadata.callback(
            "headers", "x-token", str, container
        )
        assert header_one == "abc"

        pattern = Pattern().metadata.callback(
            "pattern", None, str, container
        )
        assert pattern == "ping"

        rpc_ctx = Ctx().metadata.callback(
            "ctx", None, object, container
        )
        assert rpc_ctx.get_pattern() == "ping"

        request_obj = Context().metadata.callback(
            "request", None, object, container
        )
        assert request_obj is req
    finally:
        container.destroy()


def test_microservice_options_defaults():
    opt = TCPClientOption()
    assert opt.host == "localhost"
    assert opt.port == 1333
    assert Transport.TCP.value == "TCP"
