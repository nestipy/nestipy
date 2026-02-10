Resolvers define how GraphQL fields are fetched. In Nestipy, a resolver is a class decorated with `@Resolver()` and composed of `@Query()`, `@Mutation()`, and `@ResolveField()` handlers.

## Resolver Basics

```python
from typing import Annotated
from nestipy.graphql import Resolver, Query, ResolveField
from nestipy.graphql.strawberry import ObjectType
from nestipy.ioc import Arg


@ObjectType()
class Cat:
    id: str
    name: str


@Resolver(of=Cat)
class CatsResolver:
    @Query()
    async def cat(self, id: Annotated[str, Arg()]) -> Cat:
        return Cat(id=id, name="Misty")

    @ResolveField()
    async def name(self, root: Cat) -> str:
        return root.name.upper()
```

## Field Resolvers

Use `@ResolveField()` to compute a field based on the parent object. This is useful when you want to lazy-load nested data.

```python
@ResolveField()
async def owner(self, root: Cat) -> Owner:
    return await self.owner_service.find_by_cat_id(root.id)
```

## Using Guards

Resolvers support `@UseGuards()` and `ExecutionContext` just like HTTP controllers:

```python
from nestipy.common import UseGuards


@Resolver(of=Cat)
@UseGuards(AuthGuard)
class CatsResolver:
    @Query()
    async def cat(self, id: Annotated[str, Arg()]) -> Cat:
        return Cat(id=id, name="Misty")
```

## Tips

- Keep resolver logic thin and call providers for heavy logic.
- Use `ResolveField` for nested data to avoid over-fetching.
- Use guards or interceptors when access control is required.
