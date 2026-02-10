from nestipy.common import Module
from nestipy.graphql import Resolver, Query, Mutation, Subscription, ResolveField
from nestipy.graphql.graphql_explorer import GraphqlExplorer


class Cat:
    name: str


@Resolver(of=Cat)
class CatResolver:
    @Query(name="ping", description="Ping the service")
    async def ping(self) -> str:
        return "ok"

    @Mutation(name="createCat", description="Create a cat")
    async def create_cat(self) -> Cat:
        return Cat()

    @Subscription(name="catEvents", description="Cat events")
    async def cat_events(self) -> str:
        return "event"

    @ResolveField(name="nickname", description="Nickname")
    async def nickname(self, root: Cat) -> str:
        return root.name


@Module(providers=[CatResolver])
class AppModule:
    pass


def test_graphql_explorer_preserves_field_options_and_names():
    query, mutation, subscription, field_resolver = GraphqlExplorer.explore(AppModule)

    assert any(q["name"] == "ping" for q in query)
    assert any(m["name"] == "createCat" for m in mutation)
    assert any(s["name"] == "catEvents" for s in subscription)
    assert any(f["name"] == "nickname" for f in field_resolver)

    q = next(item for item in query if item["name"] == "ping")
    assert q["field_options"]["description"] == "Ping the service"
    assert "name" not in q["field_options"]

    f = next(item for item in field_resolver if item["name"] == "nickname")
    assert f["field_options"]["description"] == "Nickname"
