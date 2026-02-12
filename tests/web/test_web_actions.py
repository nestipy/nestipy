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
    build_actions_schema,
    generate_actions_client_code_from_schema,
)


@Injectable()
class DemoActions:
    @action()
    async def hello(self, name: str = "world") -> str:
        return f"Hello, {name}!"

    def __init__(self) -> None:
        self._counter = 0

    @action(cache=60)
    async def cached_counter(self) -> int:
        self._counter += 1
        return self._counter


@dataclass
class Greeting:
    message: str


@Injectable()
class TypedActions:
    @action()
    async def greet(self, name: str) -> Greeting:
        return Greeting(message=f"Hello, {name}")

    @action()
    async def add(self, a: int, b: int) -> int:
        return a + b


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

        cached_1 = await client.post(
            "/_actions",
            json={"action": "DemoActions.cached_counter", "args": [], "kwargs": {}},
        )
        assert cached_1.json() == {"ok": True, "data": 1}
        cached_2 = await client.post(
            "/_actions",
            json={"action": "DemoActions.cached_counter", "args": [], "kwargs": {}},
        )
        assert cached_2.json() == {"ok": True, "data": 1}

        invalid = await client.post(
            "/_actions",
            json={"action": "TypedActions.add", "args": ["x", 2], "kwargs": {}},
        )
        assert invalid.status() == 200
        invalid_payload = invalid.json()
        assert invalid_payload.get("ok") is False
        assert invalid_payload.get("error", {}).get("type") == "ActionValidationError"

        schema = await client.get("/_actions/schema")
        assert schema.status() == 200
        schema_json = schema.json()
        assert schema_json.get("endpoint") == "/_actions"
        assert any(a.get("name") == "DemoActions.hello" for a in schema_json.get("actions", []))
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


def test_actions_codegen_from_schema(tmp_path: Path):
    schema = build_actions_schema([AppModule], endpoint="/_actions")
    code = generate_actions_client_code_from_schema(schema)
    out = tmp_path / "actions.schema.ts"
    out.write_text(code, encoding="utf-8")
    text = out.read_text(encoding="utf-8")
    assert "DemoActions" in text
    assert "cached_counter" in text
