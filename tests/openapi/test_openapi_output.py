import pytest
from pydantic import BaseModel

from nestipy.common import Controller, Get, Post, Module
from nestipy.core import NestipyFactory
from nestipy.openapi import (
    ApiOperation,
    ApiExternalDocs,
    ApiServer,
    ApiCallbacks,
    ApiCookie,
    ApiQuery,
    ApiBearerAuth,
    ApiBadRequestResponse,
    ApiBody,
    ApiExtraModels,
)
from nestipy.openapi.openapi_docs.v3 import Callback, PathItem, ParameterLocation


class InnerDto(BaseModel):
    name: str


class OuterDto(BaseModel):
    inner: InnerDto


@Controller("/cats")
class CatsController:
    @ApiOperation(
        summary="Get cat",
        description="Fetch a single cat",
        operation_id="getCat",
    )
    @ApiExternalDocs("https://docs.example.com", "Docs")
    @ApiServer("https://api.example.com", "prod")
    @ApiCallbacks({"onEvent": Callback(expression="{$request.body#/url}", path=PathItem())})
    @ApiCookie("session_id")
    @ApiQuery("include", "Include extras", required=False)
    @ApiBearerAuth()
    @ApiBadRequestResponse()
    @Get("/{id}")
    async def get_cat(self, id: str):
        return {"id": id}

    @ApiBody(OuterDto)
    @ApiExtraModels(OuterDto)
    @Post("/")
    async def create_cat(self, payload: OuterDto):
        return payload.model_dump()


@Module(controllers=[CatsController])
class AppModule:
    pass


@pytest.mark.asyncio
async def test_openapi_output_includes_decorators():
    app = NestipyFactory.create(AppModule)
    await app.setup()

    paths = app.get_openapi_paths()
    path_item = paths["/cats/{id}"]
    op = path_item.get

    assert op is not None
    assert op.summary == "Get cat"
    assert op.description == "Fetch a single cat"
    assert op.operation_id == "getCat"
    assert op.external_docs.url == "https://docs.example.com"
    assert op.servers and op.servers[0].url == "https://api.example.com"
    assert op.callbacks and "onEvent" in op.callbacks
    assert op.security and op.security[0].name == "bearer"

    params = op.parameters or []
    assert any(p.in_ == ParameterLocation.PATH and p.name == "id" for p in params)
    assert any(
        p.in_ == ParameterLocation.COOKIE and p.name == "session_id" for p in params
    )
    assert any(p.in_ == ParameterLocation.QUERY and p.name == "include" for p in params)

    responses = op.responses
    assert 400 in responses or "400" in responses


@pytest.mark.asyncio
async def test_openapi_schemas_include_extra_models():
    app = NestipyFactory.create(AppModule)
    await app.setup()

    paths = app.get_openapi_paths()
    post_op = paths["/cats"].post
    assert post_op is not None
    assert post_op.request_body is not None
    assert "application/json" in post_op.request_body.content

    schemas = app.get_open_api_schemas()
    assert schemas is not None
    assert "schemas" in schemas
    assert "InnerDto" in schemas["schemas"]
