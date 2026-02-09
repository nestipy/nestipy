import json

import pytest

from nestipy.common import Controller, Get, Module, Injectable
from nestipy.core import NestipyFactory, NestipyConfig


@Injectable()
class CatsService:
    pass


@Controller("/cats")
class CatsController:
    @Get("/")
    async def list(self):
        return []


@Module(controllers=[CatsController], providers=[CatsService])
class AppModule:
    pass


@pytest.mark.asyncio
async def test_dependency_graph_json_dump(tmp_path):
    output = tmp_path / "deps.json"
    app = NestipyFactory.create(
        AppModule,
        NestipyConfig(dependency_graph_json_path=str(output)),
    )
    await app.setup()

    assert output.exists()
    graph = json.loads(output.read_text())
    assert "CatsService" in graph
    assert "CatsController" in graph
