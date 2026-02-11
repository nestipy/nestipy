import pytest

from nestipy.common import Controller, Module
from nestipy.common.decorator.method import Get
from nestipy.core.router.router_proxy import RouterProxy


@Controller("/dup")
class FirstController:
    @Get("/")
    def index(self):
        return {"ok": True}


@Controller("/dup")
class SecondController:
    @Get("/")
    def index(self):
        return {"ok": True}


@Module(controllers=[FirstController, SecondController])
class ConflictModule:
    pass


def test_route_conflict_detection():
    proxy = RouterProxy(router=object())
    with pytest.raises(ValueError):
        proxy.apply_routes([ConflictModule], register_routes=False, detect_conflicts=True)
