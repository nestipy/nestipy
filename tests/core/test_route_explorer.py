from nestipy.common import Controller, Get, Module
from nestipy.core.router.route_explorer import RouteExplorer


@Controller("/app")
class AppController:
    @Get("/hello")
    def get_hello(self):
        return {"message": "Hello World"}


@Module(controllers=[AppController])
class AppModule:
    pass


def test_route_explorer():
    routes = RouteExplorer.explore(AppModule)
    print(f"\nExplored routes: {routes}")
    assert len(routes) == 1
    assert routes[0]["path"] == "/app/hello"
