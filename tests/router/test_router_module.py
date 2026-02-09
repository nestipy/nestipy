from nestipy.router.router_module import RouterModule, RouteItem
from nestipy.metadata import Reflect, RouteKey


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
    Reflect.set_metadata(CatsController, RouteKey.path, "/cats")

    module = RouterModule()
    module._discover = FakeDiscover()
    module._option = [
        RouteItem(path="api", module=CatsModule),
        RouteItem(path="v1", module=CatsModule, children=[RouteItem(path="admin", module=CatsModule)]),
    ]

    module._update_router([], module._option)

    # last update wins (nested update keeps previous prefix)
    path = Reflect.get_metadata(CatsController, RouteKey.path, None)
    assert path == "v1/admin/v1/api/cats"
