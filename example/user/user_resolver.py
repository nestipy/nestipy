import asyncio
from typing import AsyncIterator, Annotated, Any

from nestipy.common import UseGuards, Request
from nestipy.graphql import Query, Resolver, Mutation
from nestipy.graphql import ResolveField
from nestipy.graphql.decorator import Subscription
from nestipy.graphql.strawberry import Info, Root
from nestipy.graphql.strawberry import ObjectType
from nestipy.ioc import Arg, Req
from .user_guards import TestGuard, TestGuardMethod


@ObjectType()
class Test:
    test1: str
    test2_named: str


@Resolver(of=Test)
@UseGuards(TestGuard)
class UserResolver:
    @Query(return_type=Test)
    @UseGuards(TestGuardMethod)
    def test_query(
        self,
        test: Annotated[str, Arg()],
        info: Annotated[Any, Info()],
        req: Annotated[Request, Req()],
    ):
        print(test, req, info)
        return Test(test1=test, test2_named="holla")

    @Mutation()
    def test_mutation(self) -> str:
        return "Mutation"

    @Subscription()
    async def test_subscription(
        self, count: Annotated[int, Arg()] = 1000
    ) -> AsyncIterator[int]:
        for i in range(count):
            yield i
            await asyncio.sleep(0.5)

    @ResolveField(name="test2_named")
    async def test2(
        self,
        root: Annotated[Any, Root()],
        info: Annotated[Any, Info()],
        req: Annotated[Request, Req()],
        test: Annotated[str, Arg()],
    ) -> str:
        return f"test2 value, test1: {root.test1}, param: {test}"
