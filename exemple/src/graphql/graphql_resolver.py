from strawberry.types import Info

from pesty.plugins.strawberry_module.decorator import Resolver, Query, Mutation


@Resolver()
class GraphqlResolver:

    @Query()
    def test_query(self, root: Info) -> str:
        return "test"

    @Mutation()
    def test_mutation(self, root: Info, name: str) -> str:
        return name
