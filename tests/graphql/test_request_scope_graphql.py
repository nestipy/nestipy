from typing import Annotated

import pytest

from nestipy.common import Injectable, Scope, Module
from nestipy.core import NestipyFactory
from nestipy.graphql import GraphqlModule, GraphqlOption, Resolver, Query
from nestipy.ioc import Inject
from nestipy.ioc import NestipyContainer
from nestipy.ioc.context_container import RequestContextContainer
from nestipy.testing import TestClient


@Injectable(scope=Scope.Request)
class RequestScopedService:
    _counter = 0

    def __init__(self):
        type(self)._counter += 1
        self.instance_id = type(self)._counter


@Resolver()
class QueryResolver:
    @Query()
    async def ping(self, service: Annotated[RequestScopedService, Inject()]) -> int:
        return service.instance_id


@Module(
    providers=[RequestScopedService, QueryResolver],
)
class AppModule(GraphqlModule):
    config = GraphqlOption(url="graphql")


@pytest.mark.asyncio
async def test_graphql_request_scope_isolated():
    NestipyContainer.clear()
    RequestContextContainer.get_instance().destroy()
    app = NestipyFactory.create(AppModule)
    await app.setup()
    client = TestClient(app)

    query = {"query": "{ ping }"}
    r1 = await client.post("/graphql", json=query)
    r2 = await client.post("/graphql", json=query)

    assert r1.status() == 200
    assert r2.status() == 200
    v1 = r1.json().get("data", {}).get("ping")
    v2 = r2.json().get("data", {}).get("ping")
    assert v1 is not None and v2 is not None
    assert v1 != v2
    NestipyContainer.clear()
    RequestContextContainer.get_instance().destroy()
