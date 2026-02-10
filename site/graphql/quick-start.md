Nestipy uses Strawberry as its GraphQL engine and exposes a NestJS-like API for resolvers, guards, interceptors, and filters. The GraphQL module integrates with the same DI container you use for HTTP.

## Install

```bash
pip install strawberry-graphql
```

## Configuration

Add `GraphqlModule` to your root module:

```python
from nestipy.common import Module
from nestipy.graphql import GraphqlModule, GraphqlOption


@Module(
    imports=[
        GraphqlModule.for_root(
            options=GraphqlOption(
                url="/graphql",
                ide="graphiql",
                auto_schema_file=None,
            )
        )
    ],
    providers=[CatsResolver],
)
class AppModule:
    pass
```

`GraphqlOption` supports:

- `url` for the GraphQL endpoint.
- `ide` for the built-in playground.
- `auto_schema_file` to write schema output to disk.
- `context_callback` for custom request context.
- `schema_option` for Strawberry `Schema` kwargs.
- `asgi_option` for Strawberry ASGI `GraphQL` kwargs.

## Basic Resolver

```python
import asyncio
from typing import AsyncIterator, Annotated, Any

from nestipy.common import UseGuards, Request
from nestipy.graphql import Query, Resolver, Mutation, ResolveField
from nestipy.graphql.decorator import Subscription
from nestipy.graphql.strawberry import Info, ObjectType
from nestipy.ioc import Arg, Req


@ObjectType()
class Test:
    test1: str
    test2: str


@Resolver(of=Test)
class UserResolver:
    @Query()
    def test_query(
        self,
        test: Annotated[str, Arg()],
        info: Annotated[Any, Info()],
        req: Annotated[Request, Req()],
    ) -> Test:
        return Test(test1="test1", test2="hello")

    @Mutation()
    def test_mutation(self) -> str:
        return "Mutation"

    @Subscription()
    async def test_subscription(self, count: Annotated[int, Arg()] = 5) -> AsyncIterator[int]:
        for i in range(count):
            yield i
            await asyncio.sleep(0.5)

    @ResolveField()
    async def test2(self, root: Test) -> str:
        return "resolved " + root.test1
```

## Advanced Options

You can pass any Strawberry options directly:

```python
from datetime import timedelta

from nestipy.graphql import GraphqlOption

GraphqlOption(
    schema_option={
        "extensions": [],
        "directives": [],
        "types": [],
    },
    asgi_option={
        "debug": True,
        "allow_queries_via_get": True,
        "connection_init_wait_timeout": timedelta(minutes=1),
    },
)
```

## Lifecycle Overview

```mermaid
flowchart TB
  A["GraphQL HTTP request"] --> B["GraphqlAdapter builds execution context"]
  B --> C["Guards"]
  C --> D["Pipes"]
  D --> E["Resolver execution"]
  E --> F["Interceptors after handler"]
  F --> G["Serialize GraphQL response"]
  G --> H["Send response"]
```

## Guards and Filters

Guards and filters work the same way as HTTP. Use `ExecutionContext.switch_to_graphql()` to access GraphQL-specific data.

## Next Steps

See the resolver, mutation, and subscription pages for deeper examples and patterns.
