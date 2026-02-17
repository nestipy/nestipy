import inspect
import time
from dataclasses import dataclass
from typing import Awaitable, Callable, Literal, Optional, TypeAlias, Annotated

from nestipy.common import Controller, Get, Response, Injectable
from nestipy.core.providers.background import BackgroundTasks
from nestipy.core.types import JsonValue
from nestipy.ioc import Inject, Res


HealthKind = Literal["liveness", "readiness", "both"]
HealthResult: TypeAlias = bool | dict[str, JsonValue] | tuple[bool, JsonValue] | JsonValue


@dataclass(slots=True)
class ReadyState:
    ready: bool = False


@dataclass(slots=True)
class HealthCheck:
    name: str
    kind: HealthKind
    check: Callable[[], HealthResult | Awaitable[HealthResult]]


@Injectable()
class HealthRegistry:
    def __init__(
        self,
        background_tasks: Annotated[BackgroundTasks, Inject()],
        ready_state: Annotated[ReadyState, Inject()],
    ) -> None:
        self._background_tasks = background_tasks
        self._ready_state = ready_state
        self._checks: list[HealthCheck] = []
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.add_check("process", lambda: True, kind="liveness")
        self.add_check("app_ready", lambda: self._ready_state.ready, kind="readiness")
        self.add_check(
            "background_tasks",
            lambda: bool(getattr(self._background_tasks, "is_running", False)),
            kind="readiness",
        )

    def add_check(
        self,
        name: str,
        check: Callable[[], HealthResult | Awaitable[HealthResult]],
        kind: HealthKind = "readiness",
    ) -> None:
        self._checks.append(HealthCheck(name=name, kind=kind, check=check))

    async def run(self, kind: HealthKind) -> tuple[bool, list[dict[str, JsonValue]]]:
        results: list[dict[str, JsonValue]] = []
        overall_ok = True
        for entry in self._checks:
            if entry.kind not in (kind, "both"):
                continue
            started = time.perf_counter()
            ok = False
            details: Optional[JsonValue] = None
            try:
                value = entry.check()
                if inspect.isawaitable(value):
                    value = await value
                if isinstance(value, tuple) and len(value) == 2:
                    ok = bool(value[0])
                    details = value[1]
                elif isinstance(value, dict):
                    ok = bool(value.get("ok", True))
                    details = value
                elif isinstance(value, bool):
                    ok = value
                else:
                    ok = bool(value)
                    details = value
            except Exception as exc:
                ok = False
                details = {"error": str(exc)}
            duration_ms = (time.perf_counter() - started) * 1000
            if not ok:
                overall_ok = False
            result: dict[str, JsonValue] = {
                "name": entry.name,
                "ok": ok,
                "duration_ms": duration_ms,
            }
            if details is not None:
                result["details"] = details
            results.append(result)
        return overall_ok, results


@Controller("/")
class HealthController:
    registry: Annotated[HealthRegistry, Inject()]

    @Get("/healthz")
    async def healthz(self, res: Response = Res()) -> dict[str, JsonValue]:
        ok, checks = await self.registry.run("liveness")
        if res is not None:
            res.status(200 if ok else 503)
        return {"status": "ok" if ok else "error", "checks": checks}

    @Get("/readyz")
    async def readyz(self, res: Response = Res()) -> dict[str, JsonValue]:
        ok, checks = await self.registry.run("readiness")
        if res is not None:
            res.status(200 if ok else 503)
        return {"status": "ok" if ok else "error", "checks": checks}


__all__ = ["HealthRegistry", "HealthController", "HealthCheck", "ReadyState"]
