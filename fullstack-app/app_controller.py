from typing import Annotated

from nestipy.common import Controller, Get
from nestipy.ioc import Inject

from app_service import AppService


@Controller("/api")
class AppController:
    service: Annotated[AppService, Inject()]

    @Get("/ping")
    async def ping(self) -> str:
        return "pong"

    @Get("/message")
    async def message(self) -> str:
        return await self.service.get()