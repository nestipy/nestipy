import asyncio
from typing import AsyncIterator, Annotated

from nestipy.common import UseGuards, Request
from nestipy.graphql import Query, Resolver, Mutation
from nestipy.graphql.decorator import Subscription
from nestipy.ioc import Arg, Req
from .user_guards import TestGuard, TestGuardMethod


@Resolver()
@UseGuards(TestGuard)
class UserResolver:

    @Query()
    @UseGuards(TestGuardMethod)
    def test_query(self, test: Annotated[str, Arg()], req: Annotated[Request, Req()]) -> str:
        print(test, req)
        return "Query"

    @Mutation()
    def test_mutation(self) -> str:
        return 'Mutation'

    @Subscription()
    async def test_subscription(self, count: Annotated[int, Arg()] = 1000) -> AsyncIterator[int]:
        for i in range(count):
            yield i
            await asyncio.sleep(0.5)
