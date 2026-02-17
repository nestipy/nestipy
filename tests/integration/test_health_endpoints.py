import pytest

from nestipy.common import Module
from nestipy.core import NestipyFactory
from nestipy.ioc import NestipyContainer
from nestipy.ioc.context_container import RequestContextContainer
from nestipy.testing import TestClient


@Module()
class AppModule:
    pass


@pytest.mark.asyncio
async def test_health_endpoints_ready(monkeypatch):
    monkeypatch.delenv("NESTIPY_HEALTH", raising=False)
    app = NestipyFactory.create(AppModule)
    await app.setup()
    app._background_tasks.is_running = True
    client = TestClient(app)
    try:
        health = await client.get("/healthz", headers={"accept": "application/json"})
        assert health.status() == 200
        health_payload = health.json()
        assert health_payload.get("status") == "ok"
        assert any(
            item.get("name") == "process" for item in health_payload.get("checks", [])
        )

        ready = await client.get("/readyz", headers={"accept": "application/json"})
        ready_payload = ready.json()
        assert ready.status() == 200, ready_payload
        assert ready_payload.get("status") == "ok"
        assert any(
            item.get("name") == "app_ready" for item in ready_payload.get("checks", [])
        )
    finally:
        NestipyContainer.clear()
        RequestContextContainer.get_instance().destroy()
