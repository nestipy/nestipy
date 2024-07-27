Currently, Nestipy uses **Strawberry** as its GraphQL ASGI. It's compatible with <b>Guards</b>, <b>Interceptor</b>
and <b>ExceptionFilter</b> . Nestipy simplifies the syntax to operate more like NestJS does with GraphQL.

### Configuration

To use GraphQL wit Nestipy, we need to add `GraphQlModule` in root module `AppModule`.

```python
from nestipy.common import Module
from nestipy.graphql import GraphqlModule, GraphqlOption


@Module(
    imports=[
        ...
        GraphqlModule.for_root(options=GraphqlOption())
        ...
    ],
    providers=[
        CatsResolver
    ]

)
class AppModule:
    pass
```

So, `CatsResolver` will be like.

```python
import asyncio
from typing import AsyncIterator, Annotated, Any

from nestipy.common import UseGuards, Request
from nestipy.graphql import Query, Resolver, Mutation
from nestipy.graphql import ResolveField
from nestipy.graphql.decorator import Subscription
from nestipy.graphql.strawberry import Info
from nestipy.graphql.strawberry import ObjectType
from nestipy.ioc import Arg, Req
from .user_guards import TestGuard, TestGuardMethod


@ObjectType()
class Test:
    test1: str
    test2: str


@Resolver(of=Test)
@UseGuards(TestGuard)
class UserResolver:

    @Query()
    @UseGuards(TestGuardMethod)
    def test_query(
            self,
            test: Annotated[str, Arg()],
            info: Annotated[Any, Info()],
            req: Annotated[Request, Req()]
    ) -> Test:
        print(test, req, info)
        return Test(test1="test1", test2="holla")

    @Mutation()
    def test_mutation(self) -> str:
        return 'Mutation'

    @Subscription()
    async def test_subscription(self, count: Annotated[int, Arg()] = 1000) -> AsyncIterator[int]:
        for i in range(count):
            yield i
            await asyncio.sleep(0.5)

    @ResolveField()
    async def test2(self, root: Test) -> str:
        return 'test2 value ' + root.test1

```

For scalar, input, etc.. we can reef to <b>[Strawberry documentation ](https://strawberry.rocks/docs)</b> and using
alias from

```python 
from nestipy.graphql.strawberry import ObjectType, Input, Field, Interface, Scalar, SchemaDirective, etc

...

...
```

Or use its from Strawberry's definition.

```python
from strawberry import type, input, interface, scalar, etc

...

...
```

Take a look **[here](https://github.com/nestipy/sample/tree/main/sample-app-graphql)** for an example.
