import strawberry
from strawberry.types import Info

from exemple.src.graphql.graphql_service import GraphqlService
from pesty.common.decorator import Inject
from pesty.plugins.strawberry_module.decorator import Resolver, Query, Mutation


@Resolver()
class GraphqlResolver:
    service: GraphqlService = Inject(GraphqlService)

    @Query()
    def test_query(self, root: Info) -> str:
        return self.service.get_test()

    @Query()
    def test_query2(self, root: Info) -> str:
        return "test2"

    @Mutation()
    def test_mutation(self, root: Info, name: str) -> str:
        return name
