from typing import AsyncGenerator

from strawberry.types import Info

from exemple.src.graphql.graphql_service import GraphqlService
from nestipy.common.decorator import Inject
from nestipy.plugins.strawberry_module.decorator import Resolver, Query, Mutation, Subscription, Type
from nestipy.plugins.strawberry_module.pubsub import PubSub, STRAWBERRY_PUB_SUB


@Type()
class Data:
    data: int


@Resolver()
class GraphqlResolver:
    service: GraphqlService = Inject(GraphqlService)
    pubSub: PubSub = Inject(STRAWBERRY_PUB_SUB)

    @Query()
    def test_query(self, root: Info) -> str:
        self.pubSub.publish('test', 'test')
        return self.service.get_test()

    @Query()
    def test_query2(self, root: Info) -> str:
        return "test2"

    @Subscription()
    async def test_subscription(self) -> AsyncGenerator[str, None]:
        return self.pubSub.asyncIterator('test')

    @Mutation()
    def test_mutation(self, root: Info, name: str) -> str:
        return name
