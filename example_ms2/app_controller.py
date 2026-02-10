from typing import Annotated

from app_service import AppService
from nestipy.common import Controller, Get, Post, Put, Delete
from nestipy.ioc import Inject, Body, Param
from nestipy.microservice import ClientProxy, Client


@Controller()
class AppController:
    service: Annotated[AppService, Inject()]
    client: Annotated[ClientProxy, Client("TEST_MICROSERVICE")]

    @Get()
    async def get(self) -> str:
        print("Sending request")
        result = await self.client.send("test2", "from client")
        print("result from microservice server :::", result)
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
