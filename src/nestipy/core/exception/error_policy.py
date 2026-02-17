from __future__ import annotations

import dataclasses
import os
import typing
from typing import Any, Optional

from nestipy.common.exception.http import HttpException
from nestipy.common.exception.message import HttpStatusMessages
from nestipy.common.exception.status import HttpStatus
from nestipy.ioc import RequestContextContainer


def _env_flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _get_debug_flag(request: Any | None = None) -> bool:
    if request is not None:
        try:
            return bool(getattr(request, "debug"))
        except Exception:
            pass
    return _env_flag("NESTIPY_DEBUG")


def _get_request_id(request: Any | None = None) -> Optional[str]:
    if request is not None:
        try:
            return getattr(request, "request_id")
        except Exception:
            return None
    return None


def _resolve_request_context() -> tuple[Optional[str], bool]:
    ctx = RequestContextContainer.get_instance().execution_context
    if ctx is not None:
        req = ctx.get_request()
        return _get_request_id(req), _get_debug_flag(req)
    return None, _get_debug_flag()


def _sanitize_details(details: Any, debug: bool) -> Any:
    if details is None:
        return None
    if debug:
        return details
    if isinstance(details, dict):
        return details
    if isinstance(details, list):
        return details
    if isinstance(details, str):
        if "\n" in details or "Traceback" in details:
            return None
        return details
    return None


def _resolve_message(ex: Exception, status: int, debug: bool) -> str:
    if isinstance(ex, HttpException) and ex.message:
        message = ex.message
    else:
        message = str(ex) if str(ex) else HttpStatusMessages.INTERNAL_SERVER_ERROR
    if not debug and status >= 500:
        return HttpStatusMessages.INTERNAL_SERVER_ERROR
    return message


def build_error_info(
    ex: Exception,
    *,
    request_id: Optional[str] = None,
    debug: Optional[bool] = None,
    status_override: Optional[int] = None,
) -> dict[str, Any]:
    if request_id is None or debug is None:
        ctx_request_id, ctx_debug = _resolve_request_context()
        if request_id is None:
            request_id = ctx_request_id
        if debug is None:
            debug = ctx_debug
    if debug is None:
        debug = _get_debug_flag()
    status = status_override
    if status is None:
        if isinstance(ex, HttpException):
            status = getattr(ex, "status_code", HttpStatus.INTERNAL_SERVER_ERROR)
        else:
            status = HttpStatus.INTERNAL_SERVER_ERROR
    if not isinstance(status, int):
        status = HttpStatus.INTERNAL_SERVER_ERROR
    message = _resolve_message(ex, status, debug)
    details = None
    if isinstance(ex, HttpException):
        details = ex.details
        if debug and details is None and getattr(ex, "track_back", None) is not None:
            try:
                details = dataclasses.asdict(ex.track_back)
            except Exception:
                details = ex.details
    elif hasattr(ex, "details"):
        details = getattr(ex, "details", None)
    details = _sanitize_details(details, debug)
    payload: dict[str, Any] = {
        "type": ex.__class__.__name__,
        "message": message,
        "status": int(status),
    }
    if details is not None:
        payload["details"] = details
    if request_id:
        payload["request_id"] = request_id
    return payload


def build_graphql_error(
    ex: Exception,
    *,
    request_id: Optional[str] = None,
    debug: Optional[bool] = None,
    status_override: Optional[int] = None,
) -> tuple[str, Optional[dict[str, Any]]]:
    info = build_error_info(
        ex, request_id=request_id, debug=debug, status_override=status_override
    )
    message = info.get("message") or HttpStatusMessages.INTERNAL_SERVER_ERROR
    extensions: dict[str, Any] = {
        "code": info.get("status"),
        "type": info.get("type"),
    }
    if "details" in info:
        extensions["details"] = info["details"]
    if info.get("request_id"):
        extensions["request_id"] = info["request_id"]
    return message, extensions or None


def request_context_info() -> tuple[Optional[str], bool]:
    return _resolve_request_context()
