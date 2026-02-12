import inspect
import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Annotated, get_args, get_origin

from pydantic import TypeAdapter, ValidationError

from nestipy.common import Controller, Post, Get, Injectable
from nestipy.common.exception.http import HttpException
from nestipy.common.exception.status import HttpStatus
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Body, Inject
from nestipy.ioc.helper import ContainerHelper
from nestipy.metadata import CtxDepKey
from nestipy.metadata import Reflect, RouteKey
from nestipy.core.providers.discover import DiscoverService
from nestipy.core.on_application_bootstrap import OnApplicationBootstrap

ACTION_METADATA = "__nestipy_web_action__"
ACTION_CACHE_TTL = "__nestipy_web_action_cache_ttl__"
ACTION_CACHE_KEY = "__nestipy_web_action_cache_key__"


@dataclass(slots=True)
class ActionsOption:
    path: str = "/_actions"
    wrap_errors: bool = True


ConfigurableModuleClass, ACTIONS_OPTION_TOKEN = (
    ConfigurableModuleBuilder[ActionsOption]().set_method("for_root").build()
)


def action(
    name: str | None = None,
    *,
    cache: float | None = None,
    key: Callable[..., str] | None = None,
):
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        setattr(fn, ACTION_METADATA, name or fn.__name__)
        if cache is not None:
            setattr(fn, ACTION_CACHE_TTL, float(cache))
        if key is not None:
            setattr(fn, ACTION_CACHE_KEY, key)
        return fn

    return decorator


@Injectable()
class ActionRegistry:
    def __init__(self) -> None:
        self._actions: dict[str, Callable[..., Any]] = {}
        self._cache: dict[str, dict[str, tuple[float, Any]]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        if name in self._actions:
            raise ValueError(f"Action '{name}' is already registered")
        self._actions[name] = fn

    def get(self, name: str) -> Callable[..., Any] | None:
        return self._actions.get(name)

    def list(self) -> list[str]:
        return sorted(self._actions.keys())

    def items(self) -> dict[str, Callable[..., Any]]:
        return dict(self._actions)

    def get_cached(self, name: str, cache_key: str) -> Any | None:
        entries = self._cache.get(name)
        if not entries:
            return None
        entry = entries.get(cache_key)
        if not entry:
            return None
        expires, value = entry
        if time.monotonic() > expires:
            entries.pop(cache_key, None)
            return None
        return value

    def set_cached(self, name: str, cache_key: str, value: Any, ttl: float) -> None:
        expires = time.monotonic() + ttl
        bucket = self._cache.setdefault(name, {})
        bucket[cache_key] = (expires, value)


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


class ActionValidationError(Exception):
    def __init__(self, message: str, details: list[dict[str, Any]]):
        super().__init__(message)
        self.message = message
        self.details = details


def _prepare_action_call(
    fn: Callable[..., Any], args: list[Any], kwargs: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    sig = inspect.signature(fn)
    call_args: list[Any] = []
    call_kwargs: dict[str, Any] = {}
    remaining_args = list(args)
    remaining_kwargs = dict(kwargs)
    errors: list[dict[str, Any]] = []

    for param in sig.parameters.values():
        if param.name == "self":
            continue
        if _is_injected_param(param.annotation):
            continue
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            if remaining_args:
                call_args.extend(remaining_args)
                remaining_args = []
            continue
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            call_kwargs.update(remaining_kwargs)
            remaining_kwargs = {}
            continue

        if remaining_args:
            value = remaining_args.pop(0)
            try:
                call_args.append(_validate_value(param.annotation, value))
            except ValidationError as exc:
                errors.append(
                    {
                        "param": param.name,
                        "message": "Invalid value",
                        "details": exc.errors(),
                    }
                )
            continue

        if param.name in remaining_kwargs:
            value = remaining_kwargs.pop(param.name)
            try:
                call_kwargs[param.name] = _validate_value(param.annotation, value)
            except ValidationError as exc:
                errors.append(
                    {
                        "param": param.name,
                        "message": "Invalid value",
                        "details": exc.errors(),
                    }
                )
            continue

        if param.default is not inspect.Parameter.empty:
            try:
                call_kwargs[param.name] = _validate_value(
                    param.annotation, param.default
                )
            except ValidationError as exc:
                errors.append(
                    {
                        "param": param.name,
                        "message": "Invalid default value",
                        "details": exc.errors(),
                    }
                )
            continue

        errors.append({"message": "Missing required parameter", "param": param.name})

    if remaining_args:
        errors.append(
            {"message": "Too many positional arguments", "count": len(remaining_args)}
        )
    if remaining_kwargs:
        errors.append(
            {
                "message": "Unexpected keyword arguments",
                "names": list(remaining_kwargs.keys()),
            }
        )

    if errors:
        raise ActionValidationError("Action validation failed", errors)

    return call_args, call_kwargs


def _validate_value(annotation: Any, value: Any) -> Any:
    if annotation is inspect.Parameter.empty:
        return value
    annotation = _unwrap_annotated(annotation)
    try:
        adapter = TypeAdapter(annotation)
    except Exception:
        return value
    return adapter.validate_python(value)


def _unwrap_annotated(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        if args:
            return args[0]
    return annotation


def _is_injected_param(annotation: Any) -> bool:
    _, dep_key = ContainerHelper.get_type_from_annotation(annotation)
    # Default annotations resolve to CtxDepKey "instance".
    # Anything else is treated as DI/context and excluded from action inputs.
    return dep_key.metadata.key != "instance"


def _get_action_cache(
    fn: Callable[..., Any],
) -> tuple[float | None, Callable[..., str] | None]:
    target = fn.__func__ if inspect.ismethod(fn) else fn
    return (
        getattr(target, ACTION_CACHE_TTL, None),
        getattr(target, ACTION_CACHE_KEY, None),
    )


def _make_cache_key(
    args: list[Any], kwargs: dict[str, Any], key_fn: Callable[..., str] | None
) -> str:
    if key_fn is not None:
        try:
            return str(key_fn(*args, **kwargs))
        except Exception:
            return json.dumps(
                {"args": args, "kwargs": kwargs}, default=str, sort_keys=True
            )
    return json.dumps({"args": args, "kwargs": kwargs}, default=str, sort_keys=True)


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
            call_args, call_kwargs = _prepare_action_call(action_fn, args, kwargs)
            cache_ttl, cache_key_fn = _get_action_cache(action_fn)
            cache_key = None
            if cache_ttl is not None and cache_ttl > 0:
                cache_key = _make_cache_key(call_args, call_kwargs, cache_key_fn)
                cached = self.registry.get_cached(str(name), cache_key)
                if cached is not None:
                    return {"ok": True, "data": cached}
            if inspect.iscoroutinefunction(action_fn):
                result = await action_fn(*call_args, **call_kwargs)
            else:
                result = action_fn(*call_args, **call_kwargs)
            if cache_ttl is not None and cache_ttl > 0 and cache_key is not None:
                self.registry.set_cached(str(name), cache_key, result, cache_ttl)
        except ActionValidationError as exc:
            if self.config.wrap_errors:
                return {
                    "ok": False,
                    "error": {
                        "message": exc.message,
                        "type": "ActionValidationError",
                        "details": exc.details,
                    },
                }
            raise HttpException(HttpStatus.BAD_REQUEST, exc.message)
        except Exception as exc:
            if self.config.wrap_errors:
                return {
                    "ok": False,
                    "error": {"message": str(exc), "type": exc.__class__.__name__},
                }
            raise

        return {"ok": True, "data": result}

    @Get("/schema")
    async def schema(self) -> dict[str, Any]:
        from nestipy.web.actions_client import build_actions_schema_from_registry

        return build_actions_schema_from_registry(
            self.registry.items(), endpoint=self.config.path
        )


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
