from typing import Annotated

import pytest

from nestipy.common import Module, PipeTransform, UsePipes, Catch, UseFilters
from nestipy.common.exception.http import HttpException
from nestipy.common.exception.status import HttpStatus
from nestipy.core import NestipyFactory
from nestipy.graphql import (
    GraphqlModule,
    GraphqlOption,
    Resolver,
    Query,
    ResolveField,
    Args,
    Context,
    Parent,
)
from nestipy.graphql.strawberry import ObjectType
from nestipy.ioc import NestipyContainer
from nestipy.ioc.context_container import RequestContextContainer
from nestipy.testing import TestClient


class UpperPipe(PipeTransform):
    async def transform(self, value, metadata):
        return str(value).upper()


@Catch(HttpException)
class MyGraphqlFilter:
    async def catch(self, exception: HttpException, host):
        return "filtered"


@ObjectType()
class User:
    id: int
    name: str


@Resolver(of=User)
class UserResolver:
    @Query()
    async def user(self, id: Annotated[int, Args("id")]) -> User:
        return User(id=id, name="placeholder")

    @ResolveField()
    async def name(self, parent: Annotated[User, Parent()]) -> str:
        return f"user-{parent.id}"


@Resolver()
class QueryResolver:
    @Query()
    @UsePipes(UpperPipe)
    async def echo(self, text: Annotated[str, Args("text")]) -> str:
        return text

    @Query()
    async def ctx_foo(self, ctx: Annotated[dict, Context()]) -> str:
        return ctx.get("foo", "")

    @Query()
    @UseFilters(MyGraphqlFilter)
    async def fail(self) -> str:
        raise HttpException(HttpStatus.BAD_REQUEST, "bad request")


@Module(
    imports=[
        GraphqlModule.for_root(
            options=GraphqlOption(
                url="/graphql",
                context_callback=lambda: {"foo": "bar"},
            )
        )
    ],
    providers=[UserResolver, QueryResolver],
)
class AppModule:
    pass


@pytest.mark.asyncio
async def test_graphql_pipeline_features():
    app = NestipyFactory.create(AppModule)
    await app.setup()
    client = TestClient(app)
    try:
        r1 = await client.post("/graphql", json={"query": "{ echo(text: \"hi\") }"})
        assert r1.status() == 200
        assert r1.json().get("data", {}).get("echo") == "HI"

        r2 = await client.post("/graphql", json={"query": "{ ctxFoo }"})
        assert r2.status() == 200
        assert r2.json().get("data", {}).get("ctxFoo") == "bar"

        r3 = await client.post("/graphql", json={"query": "{ fail }"})
        assert r3.status() == 200
        assert r3.json().get("data", {}).get("fail") == "filtered"

        r4 = await client.post(
            "/graphql",
            json={"query": "{ user(id: 3) { id name } }"},
        )
        assert r4.status() == 200
        user = r4.json().get("data", {}).get("user")
        assert user == {"id": 3, "name": "user-3"}
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()
