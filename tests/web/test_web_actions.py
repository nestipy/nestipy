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
    CsrfActionGuard,
    OriginActionGuard,
    ActionSignatureGuard,
    ActionPermissionGuard,
    ActionPermissions,
)
import hashlib
import hmac
import json
import time


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


@Injectable()
class GuardedActions:
    @action()
    async def secure(self) -> str:
        return "ok"


@Injectable()
class PermissionedActions:
    @ActionPermissions("demo:read")
    @action()
    async def gated(self) -> str:
        return "ok"


class InjectUserGuard:
    def can_activate(self, ctx) -> bool:
        if ctx.request is not None:
            ctx.request.user = {"permissions": ["demo:read"]}
        return True


@Module(
    imports=[ActionsModule.for_root(ActionsOption(path="/_actions"))],
    providers=[GuardedActions],
)
class CsrfModule:
    pass


@Module(
    imports=[
        ActionsModule.for_root(
            ActionsOption(
                path="/_actions",
                guards=[CsrfActionGuard()],
            )
        )
    ],
    providers=[GuardedActions],
)
class CsrfGuardModule:
    pass


@Module(
    imports=[
        ActionsModule.for_root(
            ActionsOption(
                path="/_actions",
                guards=[OriginActionGuard(allowed_origins=["http://127.0.0.1:8000"], allow_missing=False)],
            )
        )
    ],
    providers=[GuardedActions],
)
class OriginGuardModule:
    pass


@Module(
    imports=[
        ActionsModule.for_root(
            ActionsOption(
                path="/_actions",
                guards=[ActionSignatureGuard(secret="secret")],
            )
        )
    ],
    providers=[GuardedActions],
)
class SignatureGuardModule:
    pass


@Module(
    imports=[
        ActionsModule.for_root(
            ActionsOption(
                path="/_actions",
                guards=[ActionPermissionGuard()],
            )
        )
    ],
    providers=[PermissionedActions],
)
class PermissionGuardModule:
    pass


@Module(
    imports=[
        ActionsModule.for_root(
            ActionsOption(
                path="/_actions",
                guards=[InjectUserGuard, ActionPermissionGuard()],
            )
        )
    ],
    providers=[PermissionedActions],
)
class PermissionGuardAllowModule:
    pass


@pytest.mark.asyncio
async def test_actions_csrf_endpoint():
    app = NestipyFactory.create(CsrfModule)
    await app.setup()
    client = TestClient(app)
    try:
        response = await client.get("/_actions/csrf")
        assert response.status() == 200
        payload = response.json()
        assert payload.get("csrf")
        headers = response.get_headers()
        cookie_header = headers.get("set-cookie") or headers.get("Set-Cookie")
        assert cookie_header is not None
        assert f"csrf_token={payload['csrf']}" in cookie_header
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()


@pytest.mark.asyncio
async def test_actions_csrf_guard():
    app = NestipyFactory.create(CsrfGuardModule)
    await app.setup()
    client = TestClient(app)
    try:
        missing = await client.post(
            "/_actions",
            json={"action": "GuardedActions.secure", "args": [], "kwargs": {}},
        )
        assert missing.status() == 200
        missing_payload = missing.json()
        assert missing_payload.get("ok") is False
        assert missing_payload.get("error", {}).get("type") == "HttpException"
        token = "csrf-token"
        ok = await client.post(
            "/_actions",
            headers={"x-csrf-token": token, "cookie": f"csrf_token={token}"},
            json={"action": "GuardedActions.secure", "args": [], "kwargs": {}},
        )
        assert ok.status() == 200
        assert ok.json() == {"ok": True, "data": "ok"}
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()


@pytest.mark.asyncio
async def test_actions_origin_guard():
    app = NestipyFactory.create(OriginGuardModule)
    await app.setup()
    client = TestClient(app)
    try:
        denied = await client.post(
            "/_actions",
            headers={"origin": "http://evil.com"},
            json={"action": "GuardedActions.secure", "args": [], "kwargs": {}},
        )
        assert denied.status() == 200
        denied_payload = denied.json()
        assert denied_payload.get("ok") is False
        assert denied_payload.get("error", {}).get("type") == "HttpException"
        ok = await client.post(
            "/_actions",
            headers={"origin": "http://127.0.0.1:8000"},
            json={"action": "GuardedActions.secure", "args": [], "kwargs": {}},
        )
        assert ok.status() == 200
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()


@pytest.mark.asyncio
async def test_actions_signature_guard():
    app = NestipyFactory.create(SignatureGuardModule)
    await app.setup()
    client = TestClient(app)
    try:
        ts = int(time.time())
        nonce = "nonce-1"
        body = json.dumps({"args": [], "kwargs": {}}, sort_keys=True, separators=(",", ":"))
        message = f"GuardedActions.secure|{ts}|{nonce}|{body}"
        sig = hmac.new(b"secret", message.encode("utf-8"), hashlib.sha256).hexdigest()
        ok = await client.post(
            "/_actions",
            json={
                "action": "GuardedActions.secure",
                "args": [],
                "kwargs": {},
                "meta": {"ts": ts, "nonce": nonce, "sig": sig},
            },
        )
        assert ok.status() == 200
        assert ok.json() == {"ok": True, "data": "ok"}
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()


@pytest.mark.asyncio
async def test_actions_permission_guard():
    app = NestipyFactory.create(PermissionGuardModule)
    await app.setup()
    client = TestClient(app)
    try:
        denied = await client.post(
            "/_actions",
            json={"action": "PermissionedActions.gated", "args": [], "kwargs": {}},
        )
        assert denied.status() == 200
        denied_payload = denied.json()
        assert denied_payload.get("ok") is False
        assert denied_payload.get("error", {}).get("type") == "HttpException"
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()

    app = NestipyFactory.create(PermissionGuardAllowModule)
    await app.setup()
    client = TestClient(app)
    try:
        allowed = await client.post(
            "/_actions",
            json={"action": "PermissionedActions.gated", "args": [], "kwargs": {}},
        )
        assert allowed.status() == 200
        assert allowed.json() == {"ok": True, "data": "ok"}
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()
