from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app_service import AppService
from nestipy.common import Get, Inject
from nestipy.common.decorator.controller import Controller


@Controller()
class AppController:
    template: Jinja2Templates = Inject('TEMPLATE')
    service: AppService = Inject(AppService)

    @Get('/', response_class=HTMLResponse)
    async def login(self, request: Request):
        return self.template.TemplateResponse(request=request, name="index.html", context={"id": id})
