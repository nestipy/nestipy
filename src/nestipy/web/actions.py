import inspect
from dataclasses import dataclass
from typing import Any, Callable, Awaitable, Annotated

from nestipy.common import Controller, Post, Injectable
from nestipy.common.exception.http import HttpException
from nestipy.common.exception.status import HttpStatus
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Body, Inject
from nestipy.metadata import Reflect, RouteKey
from nestipy.core.providers.discover import DiscoverService
from nestipy.core.on_application_bootstrap import OnApplicationBootstrap

ACTION_METADATA = "__nestipy_web_action__"


@dataclass(slots=True)
class ActionsOption:
    path: str = "/_actions"
    wrap_errors: bool = True


ConfigurableModuleClass, ACTIONS_OPTION_TOKEN = (
    ConfigurableModuleBuilder[ActionsOption]().set_method("for_root").build()
)


def action(name: str | None = None):
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, ACTION_METADATA, name or fn.__name__)
        return fn

    return decorator


@Injectable()
class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        if name in self._actions:
            raise ValueError(f"Action '{name}' is already registered")
        self._actions[name] = fn

    def get(self, name: str) -> Callable[..., Any] | None:
        return self._actions.get(name)

    def list(self) -> list[str]:
        return sorted(self._actions.keys())


@Injectable()
class ActionExplorer(OnApplicationBootstrap):
    registry: Annotated[ActionRegistry, Inject()]
    discover: Annotated[DiscoverService, Inject()]

    async def on_application_bootstrap(self) -> None:
        for instance in (
            self.discover.get_all_provider() + self.discover.get_all_controller()
        ):
            self._register_actions(instance)

    def _register_actions(self, instance: Any) -> None:
        for name in dir(instance):
            if name.startswith("_"):
                continue
            try:
                value = getattr(instance, name)
            except Exception:
                continue
            action_name = _get_action_name(value)
            if not action_name:
                continue
            if "." not in action_name:
                action_name = f"{instance.__class__.__name__}.{action_name}"
            self.registry.register(action_name, value)


def _get_action_name(fn: Any) -> str | None:
    if inspect.ismethod(fn):
        return getattr(fn.__func__, ACTION_METADATA, None)
    if inspect.isfunction(fn):
        return getattr(fn, ACTION_METADATA, None)
    return getattr(fn, ACTION_METADATA, None)


@Controller("/")
class ActionsController:
    registry: Annotated[ActionRegistry, Inject()]
    config: Annotated[ActionsOption, Inject(ACTIONS_OPTION_TOKEN)]

    @Post()
    async def handle(self, payload: Annotated[dict, Body()]) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise HttpException(HttpStatus.BAD_REQUEST, "Invalid action payload")
        name = payload.get("action")
        if not name:
            raise HttpException(HttpStatus.BAD_REQUEST, "Missing action name")
        args = payload.get("args") or []
        kwargs = payload.get("kwargs") or {}
        if not isinstance(args, list) or not isinstance(kwargs, dict):
            raise HttpException(HttpStatus.BAD_REQUEST, "Invalid action arguments")
        action_fn = self.registry.get(str(name))
        if action_fn is None:
            raise HttpException(HttpStatus.NOT_FOUND, f"Action '{name}' not found")

        try:
            if inspect.iscoroutinefunction(action_fn):
                result = await action_fn(*args, **kwargs)
            else:
                result = action_fn(*args, **kwargs)
        except Exception as exc:
            if self.config.wrap_errors:
                return {
                    "ok": False,
                    "error": {"message": str(exc), "type": exc.__class__.__name__},
                }
            raise

        return {"ok": True, "data": result}


def _set_action_route(option: ActionsOption) -> None:
    if not option.path.startswith("/"):
        option.path = "/" + option.path
    Reflect.set_metadata(ActionsController, RouteKey.path, option.path)


class ActionsModule(ConfigurableModuleClass):
    config: Annotated[ActionsOption, Inject(ACTIONS_OPTION_TOKEN)]

    @classmethod
    def for_root(cls, options: ActionsOption | None = None, extras: dict | None = None):
        options = options or ActionsOption()
        _set_action_route(options)
        dynamic_module = super().for_root(options, extras=extras)
        if ActionsController not in dynamic_module.controllers:
            dynamic_module.controllers.append(ActionsController)
        if ActionRegistry not in dynamic_module.providers:
            dynamic_module.providers.append(ActionRegistry)
        if ActionExplorer not in dynamic_module.providers:
            dynamic_module.providers.append(ActionExplorer)
        return dynamic_module
