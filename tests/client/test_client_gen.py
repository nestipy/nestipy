from typing import Annotated, Optional

from nestipy.common import Controller, Module
from nestipy.common.decorator.method import Get, Post
from nestipy.ioc import Param, Body
from nestipy.client import generate_client


@Controller("/cats")
class CatsController:
    @Get("/{id}")
    def get_cat(self, cat_id: Annotated[int, Param("id")]) -> dict:
        return {"id": cat_id}

    @Post("/")
    def create_cat(self, payload: Annotated[dict, Body()]) -> dict:
        return payload


@Module(controllers=[CatsController])
class CatsModule:
    pass


def test_generate_client_writes_typescript(tmp_path):
    output = tmp_path / "api_client.ts"
    generate_client([CatsModule], str(output), class_name="ApiClient")

    assert output.is_file()
    content = output.read_text(encoding="utf-8")
    assert "ApiClient" in content
    # generated TS exposes a client surface for the controller methods
    assert "CatsController" in content or "getCat" in content or "get_cat" in content


def test_generate_client_creates_parent_dirs(tmp_path):
    output = tmp_path / "nested" / "dir" / "client.ts"
    generate_client([CatsModule], str(output))
    assert output.is_file()
