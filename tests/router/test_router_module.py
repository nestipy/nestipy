import typing

from nestipy.core.providers.discover import DiscoverService
from nestipy.metadata import Reflector, RouteKey
from nestipy.router.router_module import RouteItem, RouterModule


class CatsController:
    pass


class CatsModule:
    pass


class FakeDiscover:
    def get_module_controllers(self, module):
        if module is CatsModule:
            return [CatsController]
        return []


def test_router_module_normalize_path():
    assert RouterModule._normalize_path("/cats/") == "cats"
    assert RouterModule._normalize_path("cats") == "cats"


def test_router_module_update_router_paths():
    Reflector.set_metadata(CatsController, RouteKey.path, "/cats")

    module = RouterModule()
    module._discover = typing.cast(DiscoverService, FakeDiscover())
    module._option = [
        RouteItem(path="api", module=CatsModule),
        RouteItem(
            path="v1",
            module=CatsModule,
            children=[RouteItem(path="admin", module=CatsModule)],
        ),
    ]

    module._update_router([], module._option)

    # last update wins (nested update keeps previous prefix)
    path = Reflector.get_metadata(CatsController, RouteKey.path, None)
    assert path == "v1/admin/v1/api/cats"
