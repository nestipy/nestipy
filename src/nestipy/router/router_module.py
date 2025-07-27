from typing import Annotated

from nestipy.common import Module
from nestipy.core import DiscoverService
from nestipy.dynamic_module import NestipyModule
from nestipy.ioc import Inject
from nestipy.metadata import RouteKey, Reflect
from .router_builder import ConfigurableClassBuilder, ROUTER_CONFIG, RouteItem


@Module()
class RouterModule(ConfigurableClassBuilder, NestipyModule):
    _option: Annotated[list[RouteItem], Inject(ROUTER_CONFIG)]
    _discover: Annotated[DiscoverService, Inject()]

    async def on_startup(self):
        self._update_router([], self._option)

    def _update_router(self, main_path: [], items: list[RouteItem]):
        for item in items:
            parent_path = [*main_path]
            controllers = self._discover.get_module_controllers(item.module)
            for controller in controllers:
                controller_path = self._normalize_path(
                    Reflect.get_metadata(controller, RouteKey.path, "")
                )
                Reflect.set_metadata(
                    controller,
                    RouteKey.path,
                    "/".join(
                        [self._normalize_path(p) for p in parent_path]
                        + [self._normalize_path(item.path), controller_path]
                    ),
                )
            parent_path.append(item.path)
            if item.children:
                self._update_router(parent_path, item.children)

    @classmethod
    def register(cls, config: list[RouteItem]):
        return cls._register(config)

    @classmethod
    def _normalize_path(cls, path: str) -> str:
        return path.strip("/")
