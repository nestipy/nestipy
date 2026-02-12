from dataclasses import dataclass
from pathlib import Path

import pytest

from nestipy.common import Module, Injectable
from nestipy.core import NestipyFactory
from nestipy.ioc import NestipyContainer
from nestipy.ioc.context_container import RequestContextContainer
from nestipy.testing import TestClient
from nestipy.web import (
    ActionsModule,
    ActionsOption,
    action,
    write_actions_client_file,
)


@Injectable()
class DemoActions:
    @action()
    async def hello(self, name: str = "world") -> str:
        return f"Hello, {name}!"


@dataclass
class Greeting:
    message: str


@Injectable()
class TypedActions:
    @action()
    async def greet(self, name: str) -> Greeting:
        return Greeting(message=f"Hello, {name}")


@Module(
    imports=[ActionsModule.for_root(ActionsOption(path="/_actions"))],
    providers=[DemoActions, TypedActions],
)
class AppModule:
    pass


@pytest.mark.asyncio
async def test_actions_rpc():
    app = NestipyFactory.create(AppModule)
    await app.setup()
    client = TestClient(app)
    try:
        response = await client.post(
            "/_actions",
            json={"action": "DemoActions.hello", "args": ["Nestipy"], "kwargs": {}},
        )
        assert response.status() == 200
        payload = response.json()
        assert payload == {"ok": True, "data": "Hello, Nestipy!"}
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()


def test_actions_codegen(tmp_path: Path):
    output = tmp_path / "actions.client.ts"
    write_actions_client_file([AppModule], str(output), endpoint="/_actions")
    content = output.read_text(encoding="utf-8")
    assert "createActions" in content
    assert "Greeting" in content
    assert "TypedActions" in content
