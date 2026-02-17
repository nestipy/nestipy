# Health Checks

Nestipy ships with built-in liveness and readiness endpoints when health checks are enabled
(default). The framework exposes:

- `GET /healthz` for liveness
- `GET /readyz` for readiness

Example response:

```json
{
  "status": "ok",
  "checks": [
    { "name": "process", "ok": true, "duration_ms": 0.1 },
    { "name": "app_ready", "ok": true, "duration_ms": 0.0 },
    { "name": "background_tasks", "ok": true, "duration_ms": 0.0 }
  ]
}
```

## Adding Custom Checks

Register checks through `HealthRegistry`. You can do this during module init so checks are
ready before the app starts serving traffic.

```py
from nestipy.common import Injectable, Module
from nestipy.core import HealthRegistry, OnModuleInit


@Injectable()
class DatabaseHealth(OnModuleInit):
    def __init__(self, registry: HealthRegistry) -> None:
        self._registry = registry

    async def on_module_init(self) -> None:
        self._registry.add_check("database", self._check_db, kind="readiness")

    async def _check_db(self) -> tuple[bool, dict]:
        ok = await self._ping_db()
        return ok, {"ok": ok}

    async def _ping_db(self) -> bool:
        return True


@Module(providers=[DatabaseHealth])
class AppModule:
    pass
```

Checks can return:

- `bool` (simple pass/fail)
- `dict` (includes a payload)
- `(bool, payload)` tuple

## Disable Health Endpoints

Disable health endpoints in configuration or via environment flags:

- `NestipyConfig(health_enabled=False)`
- `NESTIPY_HEALTH=0`
