from typing import Any

from pydantic import BaseModel

from nestipy.metadata import Reflect
from nestipy.openapi import (
    ApiOperation,
    ApiSummary,
    ApiDescription,
    ApiDeprecated,
    ApiExternalDocs,
    ApiServer,
    ApiServers,
    ApiCallbacks,
    ApiExtraModels,
    ApiParam,
    ApiCookie,
)
from nestipy.openapi.openapi_docs.v3 import Server, Callback, PathItem


def test_openapi_operation_metadata():
    def handler():
        return None

    handler = ApiSummary("Sum")(handler)
    handler = ApiDescription("Desc")(handler)
    handler = ApiDeprecated()(handler)
    handler = ApiOperation(
        summary="Sum2", description="Desc2", deprecated=True, operation_id="op"
    )(handler)

    meta = Reflect.get(handler)
    assert meta["__openapi__summary"] == "Sum2"
    assert meta["__openapi__description"] == "Desc2"
    assert meta["__openapi__deprecated"] is True
    assert meta["__openapi__operation_id"] == "op"


def test_openapi_external_docs_and_servers_and_callbacks():
    def handler():
        return None

    handler = ApiExternalDocs("https://example.com", "Docs")(handler)
    handler = ApiServer("https://api.example.com", "prod")(handler)
    handler = ApiServers([Server(url="https://staging.example.com")])(handler)

    callbacks = {"cb": Callback(expression="{$request.body#/url}", path=PathItem())}
    handler = ApiCallbacks(callbacks)(handler)

    meta = Reflect.get(handler)
    assert meta["__openapi__external_docs"].url == "https://example.com"
    assert len(meta["__openapi__servers"]) == 2
    assert "cb" in meta["__openapi__callbacks"].keys()


def test_openapi_extra_models_and_params():
    class Inner(BaseModel):
        name: str

    class Outer(BaseModel):
        inner: Inner

    def handler():
        return None

    handler = ApiExtraModels(Outer)(handler)
    handler = ApiParam("id")(handler)
    handler = ApiCookie("session_id")(handler)

    meta = Reflect.get(handler)
    schemas = meta.get("__openapi__schemas", {})
    assert isinstance(schemas, dict)
    assert len(schemas) > 0

    params = meta.get("__openapi__parameters", [])
    assert len(params) == 2
