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
from typing import AsyncIterator

from nestipy.graphql import Resolver, Query, Mutation, Subscription
from nestipy.types_ import Args


@Resolver()
class CatsResolver:
    @Query()
    @UseGuards(TestGuardMethod)
    def test_query(self, test: Args[str]) -> str:
        return "Query"

    @Mutation()
    def test_mutation(self) -> str:
        return 'Mutation'

    @Subscription()
    async def test_subscription(self, count: Args[int] = 1000) -> AsyncIterator[int]:
        for i in range(count):
            yield i
            await asyncio.sleep(0.5)
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
