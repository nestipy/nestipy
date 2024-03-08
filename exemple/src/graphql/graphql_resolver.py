from typing import AsyncGenerator

from strawberry.types import Info
from datetime import datetime

from nestipy.common import UseGuards
from .graphql_service import GraphqlService
from nestipy.common.decorator import Inject
from nestipy.plugins.strawberry_module.decorator import Resolver, Query, Mutation, Subscription, Type
from nestipy.plugins.strawberry_module.pubsub import PubSub, STRAWBERRY_PUB_SUB
from ..guard.auth_guard import AuthGuard


@Type()
class Data:
    data: int


class Metadata:
    def __init__(self, metadata: list = None):
        self.metadata = metadata

    def __call__(self, cls):
        setattr(cls, 'metadata__guards__', self.metadata or [])
        return cls


@Resolver()
class GraphqlResolver:
    service: GraphqlService = Inject(GraphqlService)
    pubSub: PubSub = Inject(STRAWBERRY_PUB_SUB)

    @Query()
    @UseGuards(AuthGuard)
    @Metadata(metadata=['test_query'])
    def test_query(self) -> str:
        self.pubSub.publish('test', f"test::{datetime.now().timestamp()}")
        return self.service.get_test()

    @Query()
    @Metadata(metadata=['test_query2'])
    def test_query2(self, root: Info) -> str:
        return "test2"

    @Subscription()
    async def test_subscription(self) -> AsyncGenerator[str, None]:
        return self.pubSub.asyncIterator('test')

    @Mutation()
    def test_mutation(self, root: Info, name: str) -> str:
        return name
