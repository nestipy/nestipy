Mutations change data and return a result. They are defined with `@Mutation()` inside a resolver class.

## Basic Mutation

```python
from dataclasses import dataclass
from typing import Annotated

from nestipy.graphql import Resolver, Mutation
from nestipy.graphql.strawberry import ObjectType
from nestipy.ioc import Arg


@ObjectType()
class Cat:
    id: str
    name: str


@dataclass
class CreateCatInput:
    name: str


@Resolver(of=Cat)
class CatsResolver:
    @Mutation()
    async def create_cat(self, input: Annotated[CreateCatInput, Arg()]) -> Cat:
        return Cat(id="1", name=input.name)
```

## Validation and Services

For complex input validation, combine mutations with pipes or validation inside your service layer.

```python
@Mutation()
async def create_cat(self, input: Annotated[CreateCatInput, Arg()]) -> Cat:
    return await self.cats_service.create(input)
```

## Tips

- Keep mutations small and delegate logic to providers.
- Return a meaningful result object rather than raw primitives when possible.
