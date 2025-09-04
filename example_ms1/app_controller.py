from typing import Annotated, Union, Awaitable

from app_service import AppService
from nestipy.common import (
    Controller,
    Post,
    Put,
    Delete,
    CanActivate,
    Injectable,
    UseGuards,
    Catch,
    UseFilters,
)
from nestipy.core import ExecutionContext, ArgumentHost
from nestipy.ioc import Inject, Body, Param
from nestipy.microservice import MessagePattern, RpcExceptionFilter, RpcException
from nestipy.microservice import Payload, RPCErrorCode, RPCErrorMessage


@Injectable()
class TestGuard(CanActivate):
    def can_activate(self, context: "ExecutionContext") -> Union[Awaitable[bool], bool]:
        print(" Guards data :::", context.switch_to_rpc().get_data())
        return True


@Catch(RpcException)
class MyRpcExceptionFilter(RpcExceptionFilter):
    async def catch(self, exception: "RpcException", host: "ArgumentHost"):
        return exception.message


@Controller()
class AppController:
    service: Annotated[AppService, Inject()]

    @UseGuards(TestGuard)
    @MessagePattern("test")
    async def get(self, data: Annotated[str, Payload()]) -> str:
        print("Event data ::", data)
        return await self.service.get()

    @UseFilters(MyRpcExceptionFilter)
    @MessagePattern("test2")
    async def get2(self, data: Annotated[str, Payload()]) -> str:
        print("Event data ::", data)
        # raise RpcException(RPCErrorCode.ABORTED, RPCErrorMessage.ABORTED)
        return "Hello"

    @Post()
    async def post(self, data: Annotated[dict, Body()]) -> str:
        return await self.service.post(data=data)

    @Put("/{app_id}")
    async def put(
        self, app_id: Annotated[int, Param("app_id")], data: Annotated[dict, Body()]
    ) -> str:
        return await self.service.put(id_=app_id, data=data)

    @Delete("/{app_id}")
    async def delete(self, app_id: Annotated[int, Param("app_id")]) -> None:
        await self.service.delete(id_=app_id)
