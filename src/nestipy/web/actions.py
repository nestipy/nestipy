import inspect
import json
import time
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Annotated, get_args, get_origin, Protocol, Iterable
from urllib.parse import urlparse
import hashlib
import hmac
import secrets

from pydantic import TypeAdapter, ValidationError

from nestipy.common import Controller, Post, Get, Injectable, Request, Response
from nestipy.common.exception.http import HttpException
from nestipy.common.exception.status import HttpStatus
from nestipy.common.logger import logger
from nestipy.core.exception.error_policy import build_error_info
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Body, Inject, Req, Res, NestipyContainer
from nestipy.ioc.helper import ContainerHelper
from nestipy.metadata import CtxDepKey, SetMetadata
from nestipy.metadata import Reflect, RouteKey
from nestipy.core.providers.discover import DiscoverService
from nestipy.core.on_application_bootstrap import OnApplicationBootstrap

ACTION_METADATA = "__nestipy_web_action__"
ACTION_CACHE_TTL = "__nestipy_web_action_cache_ttl__"
ACTION_CACHE_KEY = "__nestipy_web_action_cache_key__"
ACTION_GUARDS = "__nestipy_web_action_guards__"
ACTION_PERMISSIONS = "__nestipy_web_action_permissions__"


@dataclass(slots=True)
class ActionContext:
    """Context passed to action guards."""
    action: str
    action_fn: Callable[..., Any] | None
    payload: dict[str, Any]
    args: list[Any]
    kwargs: dict[str, Any]
    request: Request | None = None

    @property
    def headers(self) -> dict[str, Any]:
        return self.request.headers if self.request is not None else {}

    @property
    def user(self) -> Any:
        return self.request.user if self.request is not None else None


class ActionGuard(Protocol):
    """Guard protocol for actions."""

    def can_activate(self, ctx: ActionContext) -> Any:
        ...


@dataclass
class ActionNonceCache:
    """In-memory nonce cache for replay protection."""
    ttl_seconds: int = 300
    _entries: dict[str, float] = field(default_factory=dict)

    def _cleanup(self) -> None:
        now = time.time()
        expired = [nonce for nonce, exp in self._entries.items() if exp <= now]
        for nonce in expired:
            self._entries.pop(nonce, None)

    def add(self, nonce: str) -> None:
        self._cleanup()
        self._entries[nonce] = time.time() + self.ttl_seconds

    def seen(self, nonce: str) -> bool:
        self._cleanup()
        return nonce in self._entries


class OriginActionGuard:
    """Validate request Origin/Referer against an allow-list."""

    def __init__(
        self,
        *,
        allowed_origins: Iterable[str] | None = None,
        allow_missing: bool = False,
        allow_same_origin: bool = True,
    ) -> None:
        self.allowed_origins = {o.rstrip("/") for o in (allowed_origins or [])}
        self.allow_missing = allow_missing
        self.allow_same_origin = allow_same_origin

    def _origin_from_header(self, value: str) -> str | None:
        if not value:
            return None
        if value.startswith("http://") or value.startswith("https://"):
            parsed = urlparse(value)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
        return None

    def can_activate(self, ctx: ActionContext) -> bool:
        if ctx.request is None:
            return True
        origin = ctx.headers.get("origin") or ""
        referer = ctx.headers.get("referer") or ctx.headers.get("referrer") or ""
        origin_value = self._origin_from_header(origin) or self._origin_from_header(referer)
        if not origin_value:
            return self.allow_missing
        origin_value = origin_value.rstrip("/")
        if origin_value in self.allowed_origins:
            return True
        if self.allow_same_origin and ctx.request.host:
            return origin_value == ctx.request.host.rstrip("/")
        return False


class CsrfActionGuard:
    """Validate CSRF token from header/payload against cookie/session."""

    def __init__(
        self,
        *,
        header: str = "x-csrf-token",
        cookie: str = "csrf_token",
        meta_key: str = "csrf",
        allow_missing: bool = False,
        allow_missing_origin: bool = False,
    ) -> None:
        self.header = header.lower()
        self.cookie = cookie
        self.meta_key = meta_key
        self.allow_missing = allow_missing
        self.allow_missing_origin = allow_missing_origin

    def can_activate(self, ctx: ActionContext) -> bool:
        if ctx.request is None:
            return True
        origin = (
            ctx.headers.get("origin")
            or ctx.headers.get("referer")
            or ctx.headers.get("referrer")
            or ""
        )
        if not origin and self.allow_missing_origin:
            return True
        header_value = ctx.headers.get(self.header)
        meta = ctx.payload.get("meta") if isinstance(ctx.payload, dict) else None
        meta_value = meta.get(self.meta_key) if isinstance(meta, dict) else None
        token = header_value or meta_value
        if not token:
            return self.allow_missing
        cookie_value = ctx.request.cookies.get(self.cookie)
        if cookie_value and secrets.compare_digest(str(cookie_value), str(token)):
            return True
        return False


class ActionSignatureGuard:
    """Validate HMAC signatures for action payloads with replay protection."""

    def __init__(
        self,
        *,
        secret: str | bytes,
        ttl_seconds: int = 300,
        header_ts: str = "x-action-ts",
        header_nonce: str = "x-action-nonce",
        header_sig: str = "x-action-signature",
        meta_ts: str = "ts",
        meta_nonce: str = "nonce",
        meta_sig: str = "sig",
        allow_payload_meta: bool = True,
        nonce_cache: ActionNonceCache | None = None,
    ) -> None:
        self.secret = secret.encode() if isinstance(secret, str) else secret
        self.ttl_seconds = ttl_seconds
        self.header_ts = header_ts.lower()
        self.header_nonce = header_nonce.lower()
        self.header_sig = header_sig.lower()
        self.meta_ts = meta_ts
        self.meta_nonce = meta_nonce
        self.meta_sig = meta_sig
        self.allow_payload_meta = allow_payload_meta
        self.nonce_cache = nonce_cache or ActionNonceCache(ttl_seconds=ttl_seconds)

    def _signature_payload(self, ctx: ActionContext, ts: str, nonce: str) -> str:
        body = json.dumps(
            {"args": ctx.args, "kwargs": ctx.kwargs},
            default=str,
            sort_keys=True,
            separators=(",", ":"),
        )
        return f"{ctx.action}|{ts}|{nonce}|{body}"

    def can_activate(self, ctx: ActionContext) -> bool:
        meta = ctx.payload.get("meta") if isinstance(ctx.payload, dict) else None
        header_ts = ctx.headers.get(self.header_ts)
        header_nonce = ctx.headers.get(self.header_nonce)
        header_sig = ctx.headers.get(self.header_sig)
        meta_ts = meta.get(self.meta_ts) if isinstance(meta, dict) else None
        meta_nonce = meta.get(self.meta_nonce) if isinstance(meta, dict) else None
        meta_sig = meta.get(self.meta_sig) if isinstance(meta, dict) else None

        ts = header_ts or (meta_ts if self.allow_payload_meta else None)
        nonce = header_nonce or (meta_nonce if self.allow_payload_meta else None)
        sig = header_sig or (meta_sig if self.allow_payload_meta else None)

        if not ts or not nonce or not sig:
            return False

        try:
            ts_value = float(ts)
        except Exception:
            return False

        if abs(time.time() - ts_value) > self.ttl_seconds:
            return False

        if self.nonce_cache.seen(str(nonce)):
            return False
        self.nonce_cache.add(str(nonce))

        message = self._signature_payload(ctx, str(ts), str(nonce)).encode("utf-8")
        expected = hmac.new(self.secret, message, hashlib.sha256).hexdigest()
        return secrets.compare_digest(expected, str(sig))


@dataclass(slots=True)
class ActionsOption:
    """Options to configure the actions controller and schema."""
    path: str = "/_actions"
    wrap_errors: bool = True
    guards: list[Any] = field(default_factory=list)
    csrf_enabled: bool = True
    csrf_endpoint: str = "/csrf"
    csrf_cookie: str = "csrf_token"
    csrf_cookie_path: str = "/"
    csrf_cookie_samesite: str = "Lax"
    csrf_cookie_secure: bool = False
    csrf_cookie_http_only: bool = False
    csrf_token_bytes: int = 32


ConfigurableModuleClass, ACTIONS_OPTION_TOKEN = (
    ConfigurableModuleBuilder[ActionsOption]().set_method("for_root").build()
)


def action(
    name: str | None = None,
    *,
    cache: float | None = None,
    key: Callable[..., str] | None = None,
):
    """Mark a method as a web action with optional caching metadata."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        """Attach action metadata to the callable."""
        setattr(fn, ACTION_METADATA, name or fn.__name__)
        if cache is not None:
            setattr(fn, ACTION_CACHE_TTL, float(cache))
        if key is not None:
            setattr(fn, ACTION_CACHE_KEY, key)
        return fn

    return decorator


def UseActionGuards(*guards: Any):
    """Attach guards to an action function."""
    valid = [g for g in guards if g is not None]
    return SetMetadata(ACTION_GUARDS, valid, as_list=True)


def ActionPermissions(*permissions: str):
    """Attach required permissions to an action function."""
    perms = [p for p in permissions if p]
    return SetMetadata(ACTION_PERMISSIONS, perms, as_list=True)


def ActionAuth(
    *permissions: str,
    guards: Iterable[Any] | None = None,
    require_permissions_guard: bool = True,
):
    """Attach permissions and guards to an action in one decorator."""
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        if permissions:
            fn = ActionPermissions(*permissions)(fn)
        guard_list: list[Any] = list(guards or [])
        if permissions and require_permissions_guard:
            guard_list.insert(0, ActionPermissionGuard)
        if guard_list:
            fn = UseActionGuards(*guard_list)(fn)
        return fn

    return decorator


@Injectable()
class ActionRegistry:
    """Store action callables and optional cache entries."""
    def __init__(self) -> None:
        """Initialize action registry storage."""
        self._actions: dict[str, Callable[..., Any]] = {}
        self._cache: dict[str, dict[str, tuple[float, Any]]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        """Register a new action callable."""
        if name in self._actions:
            raise ValueError(f"Action '{name}' is already registered")
        self._actions[name] = fn

    def get(self, name: str) -> Callable[..., Any] | None:
        """Fetch a registered action by name."""
        return self._actions.get(name)

    def list(self) -> list[str]:
        """List registered action names."""
        return sorted(self._actions.keys())

    def items(self) -> dict[str, Callable[..., Any]]:
        """Return a copy of the action registry."""
        return dict(self._actions)

    def get_cached(self, name: str, cache_key: str) -> Any | None:
        """Retrieve a cached action response if still valid."""
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
        """Store a cached action response with a TTL."""
        expires = time.monotonic() + ttl
        bucket = self._cache.setdefault(name, {})
        bucket[cache_key] = (expires, value)


@Injectable()
class ActionExplorer(OnApplicationBootstrap):
    """Discover action methods after application bootstrap."""
    registry: Annotated[ActionRegistry, Inject()]
    discover: Annotated[DiscoverService, Inject()]

    async def on_application_bootstrap(self) -> None:
        """Register actions found in providers and controllers."""
        for instance in (
            self.discover.get_all_provider() + self.discover.get_all_controller()
        ):
            self._register_actions(instance)

    def _register_actions(self, instance: Any) -> None:
        """Inspect an instance and register any decorated actions."""
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
    """Extract the action name metadata from a callable."""
    if inspect.ismethod(fn):
        return getattr(fn.__func__, ACTION_METADATA, None)
    if inspect.isfunction(fn):
        return getattr(fn, ACTION_METADATA, None)
    return getattr(fn, ACTION_METADATA, None)


def _get_action_guards(fn: Any) -> list[Any]:
    """Extract guard metadata from a callable."""
    target = fn.__func__ if inspect.ismethod(fn) else fn
    return Reflect.get_metadata(target, ACTION_GUARDS, []) or []


def _get_action_permissions(fn: Any) -> list[str]:
    target = fn.__func__ if inspect.ismethod(fn) else fn
    return Reflect.get_metadata(target, ACTION_PERMISSIONS, []) or []


def _extract_user_permissions(user: Any) -> set[str]:
    if user is None:
        return set()
    if isinstance(user, dict) and "permissions" in user:
        perms = user.get("permissions") or []
    elif hasattr(user, "permissions"):
        perms = getattr(user, "permissions")
    elif hasattr(user, "get_permissions"):
        try:
            perms = user.get_permissions()
        except Exception:
            perms = []
    else:
        perms = []
    if isinstance(perms, str):
        return {perms}
    if isinstance(perms, Iterable):
        return {str(p) for p in perms}
    return set()


class ActionPermissionGuard:
    """Ensure the current user has required action permissions."""

    def __init__(self, *, require_all: bool = True) -> None:
        self.require_all = require_all

    def can_activate(self, ctx: ActionContext) -> bool:
        if ctx.action_fn is None:
            return True
        required = _get_action_permissions(ctx.action_fn)
        if not required:
            return True
        user_perms = _extract_user_permissions(ctx.user)
        if self.require_all:
            return all(p in user_perms for p in required)
        return any(p in user_perms for p in required)


async def _resolve_guard_instance(guard: Any) -> Any:
    """Resolve a guard instance using DI when possible."""
    if inspect.isclass(guard):
        try:
            return await NestipyContainer.get_instance().get(guard)
        except Exception:
            return guard()
    return guard


async def _run_action_guards(
    guards: list[Any], ctx: ActionContext
) -> None:
    """Execute all action guards in order."""
    for guard in guards:
        instance = await _resolve_guard_instance(guard)
        if hasattr(instance, "can_activate"):
            result = instance.can_activate(ctx)
        else:
            result = instance(ctx)
        if inspect.isawaitable(result):
            result = await result
        if not result:
            raise HttpException(HttpStatus.FORBIDDEN, "Action access denied")


class ActionValidationError(Exception):
    def __init__(self, message: str, details: list[dict[str, Any]]):
        """Capture validation error details for action inputs."""
        super().__init__(message)
        self.message = message
        self.details = details


def _prepare_action_call(
    fn: Callable[..., Any], args: list[Any], kwargs: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    """Validate inputs and build positional/keyword arguments for an action call."""
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
    """Validate a value against an annotation using Pydantic if possible."""
    if annotation is inspect.Parameter.empty:
        return value
    annotation = _unwrap_annotated(annotation)
    try:
        adapter = TypeAdapter(annotation)
    except Exception:
        return value
    return adapter.validate_python(value)


def _unwrap_annotated(annotation: Any) -> Any:
    """Strip typing.Annotated wrappers from an annotation."""
    origin = get_origin(annotation)
    if origin is Annotated:
        args = get_args(annotation)
        if args:
            return args[0]
    return annotation


def _is_injected_param(annotation: Any) -> bool:
    """Check whether the annotation represents a DI/context parameter."""
    _, dep_key = ContainerHelper.get_type_from_annotation(annotation)
    # Default annotations resolve to CtxDepKey "instance".
    # Anything else is treated as DI/context and excluded from action inputs.
    return dep_key.metadata.key != "instance"


def _get_action_cache(
    fn: Callable[..., Any],
) -> tuple[float | None, Callable[..., str] | None]:
    """Read caching metadata from an action function."""
    target = fn.__func__ if inspect.ismethod(fn) else fn
    return (
        getattr(target, ACTION_CACHE_TTL, None),
        getattr(target, ACTION_CACHE_KEY, None),
    )


def _make_cache_key(
    args: list[Any], kwargs: dict[str, Any], key_fn: Callable[..., str] | None
) -> str:
    """Create a stable cache key from arguments and optional key function."""
    if key_fn is not None:
        try:
            return str(key_fn(*args, **kwargs))
        except Exception:
            return json.dumps(
                {"args": args, "kwargs": kwargs}, default=str, sort_keys=True
            )
    return json.dumps({"args": args, "kwargs": kwargs}, default=str, sort_keys=True)


def _build_csrf_cookie(
    name: str,
    value: str,
    *,
    path: str = "/",
    same_site: str = "Lax",
    secure: bool = False,
    http_only: bool = False,
) -> str:
    """Build a Set-Cookie string for CSRF tokens."""
    parts = [f"{name}={value}", f"Path={path}", f"SameSite={same_site}"]
    if secure:
        parts.append("Secure")
    if http_only:
        parts.append("HttpOnly")
    return "; ".join(parts)


@Controller("/")
class ActionsController:
    """HTTP controller that executes registered actions."""
    registry: Annotated[ActionRegistry, Inject()]
    config: Annotated[ActionsOption, Inject(ACTIONS_OPTION_TOKEN)]

    @Post()
    async def handle(
        self,
        payload: Annotated[dict, Body()],
        req: Annotated[Request, Req()] = None,
    ) -> dict[str, Any]:
        """Execute an action from the request payload."""
        start = time.perf_counter()
        ok = False
        action_name = "unknown"
        request_id = req.request_id if req is not None else None
        debug = req.debug if req is not None else False
        try:
            if not isinstance(payload, dict):
                raise HttpException(HttpStatus.BAD_REQUEST, "Invalid action payload")
            name = payload.get("action")
            if not name:
                raise HttpException(HttpStatus.BAD_REQUEST, "Missing action name")
            action_name = str(name)
            args = payload.get("args") or []
            kwargs = payload.get("kwargs") or {}
            if not isinstance(args, list) or not isinstance(kwargs, dict):
                raise HttpException(HttpStatus.BAD_REQUEST, "Invalid action arguments")
            action_fn = self.registry.get(str(name))
            if action_fn is None:
                raise HttpException(HttpStatus.NOT_FOUND, f"Action '{name}' not found")

            ctx = ActionContext(
                action=str(name),
                action_fn=action_fn,
                payload=payload,
                args=args,
                kwargs=kwargs,
                request=req,
            )
            guards = list(self.config.guards or [])
            guards.extend(_get_action_guards(action_fn))
            if guards:
                await _run_action_guards(guards, ctx)
            call_args, call_kwargs = _prepare_action_call(action_fn, args, kwargs)
            cache_ttl, cache_key_fn = _get_action_cache(action_fn)
            cache_key = None
            if cache_ttl is not None and cache_ttl > 0:
                cache_key = _make_cache_key(call_args, call_kwargs, cache_key_fn)
                cached = self.registry.get_cached(str(name), cache_key)
                if cached is not None:
                    ok = True
                    return {"ok": True, "data": cached}
            if inspect.iscoroutinefunction(action_fn):
                result = await action_fn(*call_args, **call_kwargs)
            else:
                result = action_fn(*call_args, **call_kwargs)
            if cache_ttl is not None and cache_ttl > 0 and cache_key is not None:
                self.registry.set_cached(str(name), cache_key, result, cache_ttl)
            ok = True
            return {"ok": True, "data": result}
        except ActionValidationError as exc:
            if self.config.wrap_errors:
                return {
                    "ok": False,
                    "error": build_error_info(
                        exc,
                        request_id=request_id,
                        debug=debug,
                        status_override=HttpStatus.BAD_REQUEST,
                    ),
                }
            raise HttpException(HttpStatus.BAD_REQUEST, exc.message)
        except Exception as exc:
            if self.config.wrap_errors:
                return {
                    "ok": False,
                    "error": build_error_info(
                        exc,
                        request_id=request_id,
                        debug=debug,
                    ),
                }
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "[ACTION] %s (%.2fms) ok=%s req_id=%s",
                action_name,
                duration_ms,
                ok,
                request_id,
                extra={
                    "action": action_name,
                    "duration_ms": duration_ms,
                    "ok": ok,
                    "request_id": request_id,
                },
            )

    @Get("/csrf")
    async def csrf(self, res: Annotated[Response, Res()]) -> dict[str, Any]:
        """Mint a CSRF token and set a cookie for double-submit protection."""
        if not self.config.csrf_enabled:
            raise HttpException(HttpStatus.NOT_FOUND, "CSRF endpoint disabled")
        token = secrets.token_urlsafe(self.config.csrf_token_bytes)
        cookie_value = _build_csrf_cookie(
            self.config.csrf_cookie,
            token,
            path=self.config.csrf_cookie_path,
            same_site=self.config.csrf_cookie_samesite,
            secure=self.config.csrf_cookie_secure,
            http_only=self.config.csrf_cookie_http_only,
        )
        res.header("Set-Cookie", cookie_value)
        return {"csrf": token}

    @Get("/schema")
    async def schema(
        self,
        req: Annotated[Request, Req()] = None,
        res: Annotated[Response, Res()] = None,
    ) -> dict[str, Any]:
        """Return the action schema for client generation."""
        from nestipy.web.actions_client import build_actions_schema_from_registry

        schema_cache = getattr(self, "_schema_cache", None)
        schema_etag = getattr(self, "_schema_etag", None)
        if schema_cache is None:
            schema_cache = build_actions_schema_from_registry(
                self.registry.items(), endpoint=self.config.path
            )
            payload = json.dumps(schema_cache, sort_keys=True, separators=(",", ":"))
            schema_etag = hashlib.sha256(payload.encode("utf-8")).hexdigest()
            setattr(self, "_schema_cache", schema_cache)
            setattr(self, "_schema_etag", schema_etag)

        if schema_etag and res is not None:
            res.header("ETag", f"\"{schema_etag}\"")

        if req is not None and schema_etag:
            client_etag = req.headers.get("if-none-match") or req.headers.get("If-None-Match")
            if client_etag in {schema_etag, f"\"{schema_etag}\""}:
                if res is not None:
                    res.status(304)
                return {}

        return schema_cache


def _set_action_route(option: ActionsOption) -> None:
    """Apply the configured base path to the actions controller."""
    if not option.path.startswith("/"):
        option.path = "/" + option.path
    Reflect.set_metadata(ActionsController, RouteKey.path, option.path)
    if option.csrf_endpoint:
        csrf_path = option.csrf_endpoint
        if not csrf_path.startswith("/"):
            csrf_path = "/" + csrf_path
        Reflect.set_metadata(ActionsController.csrf, RouteKey.path, csrf_path)


class ActionsModule(ConfigurableModuleClass):
    """Dynamic module that wires action discovery and endpoints."""
    config: Annotated[ActionsOption, Inject(ACTIONS_OPTION_TOKEN)]

    @classmethod
    def for_root(cls, options: ActionsOption | None = None, extras: dict | None = None):
        """Register the actions controller and providers."""
        options = options or ActionsOption()
        if not options.guards:
            security_flag = os.getenv("NESTIPY_ACTION_SECURITY", "").lower()
            enabled = security_flag not in {"0", "false", "no", "off"}
            if enabled:
                guards: list[Any] = []
                origins_env = os.getenv("NESTIPY_ACTION_ALLOWED_ORIGINS", "")
                origins = [o.strip() for o in origins_env.split(",") if o.strip()]
                allow_missing_env = os.getenv("NESTIPY_ACTION_ALLOW_MISSING_ORIGIN", "").strip()
                if allow_missing_env:
                    allow_missing = allow_missing_env.lower() in {
                        "1",
                        "true",
                        "yes",
                        "on",
                    }
                else:
                    allow_missing = True
                guards.append(
                    OriginActionGuard(
                        allowed_origins=origins,
                        allow_missing=allow_missing,
                    )
                )
                csrf_enabled = options.csrf_enabled and os.getenv("NESTIPY_ACTION_CSRF", "").lower() not in {
                    "0",
                    "false",
                    "no",
                    "off",
                }
                if csrf_enabled:
                    guards.append(
                        CsrfActionGuard(
                            cookie=options.csrf_cookie,
                            allow_missing=False,
                            allow_missing_origin=True,
                        )
                    )
                signature_secret = os.getenv("NESTIPY_ACTION_SIGNATURE_SECRET")
                if signature_secret:
                    guards.append(ActionSignatureGuard(secret=signature_secret))
                if os.getenv("NESTIPY_ACTION_PERMISSIONS", "").lower() in {
                    "1",
                    "true",
                    "yes",
                    "on",
                }:
                    guards.append(ActionPermissionGuard())
                options.guards = guards
        _set_action_route(options)
        dynamic_module = super().for_root(options, extras=extras)
        if ActionsController not in dynamic_module.controllers:
            dynamic_module.controllers.append(ActionsController)
        if ActionRegistry not in dynamic_module.providers:
            dynamic_module.providers.append(ActionRegistry)
        if ActionExplorer not in dynamic_module.providers:
            dynamic_module.providers.append(ActionExplorer)
        return dynamic_module
