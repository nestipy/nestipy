from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any, MutableMapping, Optional


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: Optional[list[str]] = None) -> list[str]:
    raw = os.getenv(name, "")
    if not raw.strip():
        return list(default or [])
    return [item.strip() for item in raw.split(",") if item.strip()]


@dataclass(slots=True)
class CorsOptions:
    allow_origins: list[str] = field(default_factory=list)
    allow_credentials: bool = False
    allow_methods: list[str] = field(
        default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    allow_headers: list[str] = field(
        default_factory=lambda: [
            "Content-Type",
            "Authorization",
            "X-Request-Id",
            "X-CSRF-Token",
            "X-Action-Ts",
            "X-Action-Nonce",
            "X-Action-Signature",
        ]
    )
    expose_headers: list[str] = field(default_factory=list)
    max_age: Optional[int] = 600
    allow_origin_regex: Optional[str] = None
    allow_all: bool = False

    @classmethod
    def from_env(cls, prefix: str = "NESTIPY_CORS") -> "CorsOptions":
        allow_all = _env_flag(f"{prefix}_ALLOW_ALL")
        allow_origins = _env_list(f"{prefix}_ORIGINS")
        allow_credentials = _env_flag(f"{prefix}_ALLOW_CREDENTIALS")
        allow_methods = _env_list(
            f"{prefix}_ALLOW_METHODS",
            default=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        )
        allow_headers = _env_list(
            f"{prefix}_ALLOW_HEADERS",
            default=[
                "Content-Type",
                "Authorization",
                "X-Request-Id",
                "X-CSRF-Token",
                "X-Action-Ts",
                "X-Action-Nonce",
                "X-Action-Signature",
            ],
        )
        expose_headers = _env_list(f"{prefix}_EXPOSE_HEADERS")
        max_age_val = os.getenv(f"{prefix}_MAX_AGE", "").strip()
        max_age = int(max_age_val) if max_age_val.isdigit() else 600
        allow_origin_regex = os.getenv(f"{prefix}_ORIGIN_REGEX")
        return cls(
            allow_origins=allow_origins,
            allow_credentials=allow_credentials,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            expose_headers=expose_headers,
            max_age=max_age,
            allow_origin_regex=allow_origin_regex,
            allow_all=allow_all,
        )


def resolve_cors_options(value: Any, *, prefix: str = "NESTIPY_CORS") -> Optional[CorsOptions]:
    if value is None:
        return None
    if isinstance(value, CorsOptions):
        return value
    if isinstance(value, dict):
        merged = CorsOptions.from_env(prefix=prefix)
        for key, val in value.items():
            if hasattr(merged, key):
                setattr(merged, key, val)
        return merged
    if isinstance(value, bool):
        if not value:
            return None
        return CorsOptions.from_env(prefix=prefix)
    return CorsOptions.from_env(prefix=prefix)


def _origin_allowed(origin: str, options: CorsOptions) -> Optional[str]:
    if options.allow_all or "*" in options.allow_origins:
        return "*"
    if origin in options.allow_origins:
        return origin
    if options.allow_origin_regex:
        try:
            if re.match(options.allow_origin_regex, origin):
                return origin
        except re.error:
            return None
    return None


def apply_cors_headers(
    headers: MutableMapping[str, str],
    origin: Optional[str],
    options: CorsOptions,
) -> None:
    if not options:
        return
    if origin is None:
        return
    allowed = _origin_allowed(origin, options)
    if not allowed:
        return
    def _set_default(key: str, value: str) -> None:
        if hasattr(headers, "setdefault"):
            headers.setdefault(key, value)
        elif key not in headers:
            headers[key] = value

    if "access-control-allow-origin" not in headers:
        headers["access-control-allow-origin"] = allowed
    if options.allow_credentials and allowed != "*":
        _set_default("access-control-allow-credentials", "true")
    _set_default("access-control-allow-methods", ", ".join(options.allow_methods))
    _set_default("access-control-allow-headers", ", ".join(options.allow_headers))
    if options.expose_headers:
        _set_default(
            "access-control-expose-headers", ", ".join(options.expose_headers)
        )
    if options.max_age is not None:
        _set_default("access-control-max-age", str(options.max_age))


__all__ = ["CorsOptions", "resolve_cors_options", "apply_cors_headers"]
