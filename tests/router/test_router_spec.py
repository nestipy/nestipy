from typing import Annotated, Optional

from nestipy.common import Controller, Module, Version, Cache, CachePolicy
from nestipy.common.decorator.method import Get, Post
from nestipy.ioc import Param, Query, Body
from nestipy.router import (
    build_router_spec,
    generate_client_code,
    generate_typescript_client_code,
)


@Controller("/cats")
class CatsController:
    @Get("/{id}")
    def get_cat(
        self,
        cat_id: Annotated[int, Param("id")],
        q: Annotated[Optional[str], Query("q")] = None,
    ) -> dict:
        return {"id": cat_id}

    @Post("/")
    def create_cat(self, payload: Annotated[dict, Body()]) -> dict:
        return payload


@Controller("/dogs")
@Version("1")
class DogsController:
    @Get("/")
    def list_dogs(self) -> list:
        return []

    @Version("2")
    @Get("/")
    def list_dogs_v2(self) -> list:
        return []

    @Cache(max_age=60, public=True)
    @Get("/cache")
    def cached_dogs(self) -> dict:
        return {"cached": True}


@Module(controllers=[CatsController])
class CatsModule:
    pass


@Module(controllers=[DogsController])
class DogsModule:
    pass


def test_build_router_spec_extracts_params():
    spec = build_router_spec([CatsModule])
    assert len(spec.routes) == 2
    get_route = next(r for r in spec.routes if r.handler == "get_cat")
    assert get_route.path == "/cats/{id}"
    assert {p.source for p in get_route.params} == {"path", "query"}
    path_param = next(p for p in get_route.params if p.source == "path")
    assert path_param.name == "id"
    query_param = next(p for p in get_route.params if p.source == "query")
    assert query_param.name == "q"


def test_generate_client_code_contains_methods():
    spec = build_router_spec([CatsModule])
    code = generate_client_code(spec, class_name="CatsClient")
    assert "class CatsClient" in code
    assert "class CatsApi" in code
    assert "def get_cat" in code
    assert "def create_cat" in code
    assert 'path = "/cats/{id}"' in code


def test_versioned_routes_are_prefixed():
    spec = build_router_spec([DogsModule])
    paths = {route.handler: route.path for route in spec.routes}
    assert paths["list_dogs"] == "/v1/dogs"
    assert paths["list_dogs_v2"] == "/v2/dogs"


def test_cache_policy_in_spec():
    spec = build_router_spec([DogsModule])
    cached = next(route for route in spec.routes if route.handler == "cached_dogs")
    assert isinstance(cached.cache, CachePolicy)
    assert cached.cache.max_age == 60
    assert cached.cache.public is True


def test_generate_typescript_client_code():
    spec = build_router_spec([CatsModule])
    code = generate_typescript_client_code(spec, class_name="CatsClient")
    assert "class CatsClient" in code
    assert "class CatsApi" in code
    assert "fetch" in code
    assert "any" not in code
