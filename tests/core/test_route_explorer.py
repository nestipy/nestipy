from nestipy.common import Controller, Get, Module
from nestipy.openapi import ApiSummary
from nestipy.core.router.route_explorer import RouteExplorer


@Controller("/app")
class AppController:
    @Get("/hello")
    def get_hello(self):
        return {"message": "Hello World"}

    @ApiSummary("Say hi")
    @Get("/hi")
    def get_hi(self):
        return {"message": "Hi"}

@Module(controllers=[AppController])
class AppModule:
    pass


def test_route_explorer():
    routes = RouteExplorer.explore(AppModule)
    print(f"\nExplored routes: {routes}")
    assert len(routes) == 2
    assert routes[0]["path"] == "/app/hello"
    hi_route = next((r for r in routes if r["method_name"] == "get_hi"), None)
    assert hi_route is not None
    assert hi_route["openapi"].get("summary") == "Say hi"
