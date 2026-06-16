from __future__ import annotations

import json
import mimetypes
import os
import re
import sys
import typing
from typing import Callable, Optional, Awaitable

import aiofiles

from nestipy.common.http_ import Request, Response
from nestipy.common.logger import logger
from nestipy.common.template import TemplateKey
from nestipy.core.types import JsonValue
from nestipy.core.adapter.http_adapter import HttpAdapter


class WebStaticHandler:
    """Serve built web assets (a Vite/SPA ``dist/``) before adapter routing."""

    def __init__(self, http_adapter: HttpAdapter) -> None:
        self._http_adapter = http_adapter
        self._try_handler: Optional[
            Callable[[Request, Response, bool], Awaitable[bool]]
        ] = None

    def register(self) -> None:
        """Register the static-file handler on the HTTP adapter."""
        dist_dir = os.getenv("NESTIPY_WEB_DIST") or ""
        if not dist_dir:
            if os.getenv("NESTIPY_WEB_DEV") == "1" or "--dev" in sys.argv:
                return
        if not dist_dir:
            argv = sys.argv[1:]

            def _cli_value(flag: str) -> Optional[str]:
                for idx, arg in enumerate(argv):
                    if arg == flag and idx + 1 < len(argv):
                        return argv[idx + 1]
                    if arg.startswith(flag + "="):
                        return arg.split("=", 1)[1]
                return None

            dist_dir = _cli_value("--web-dist") or ""
            if not dist_dir and "--web" in argv:
                candidates = ("web/dist", "src/dist", "dist")
                for candidate in candidates:
                    if os.path.isdir(candidate):
                        dist_dir = candidate
                        break
                if not dist_dir:
                    dist_dir = "web/dist"
            if dist_dir:
                os.environ["NESTIPY_WEB_DIST"] = dist_dir
            else:
                logger.info("[WEB] Static serving disabled (NESTIPY_WEB_DIST not set)")
                return
        static_dir = os.path.realpath(dist_dir)
        if not os.path.isdir(static_dir):
            logger.warning(
                "[WEB] Static dist directory not found: %s (build your frontend first)",
                static_dir,
            )
            return

        manifest_cache: dict[str, JsonValue] | None = None
        manifest_mtime: float | None = None
        manifest_assets_cache: set[str] | None = None
        hash_re = re.compile(r"[-.][a-f0-9]{8,}\.")

        static_path = os.getenv("NESTIPY_WEB_STATIC_PATH", "/").strip()
        if not static_path:
            static_path = "/"
        if not static_path.startswith("/"):
            static_path = "/" + static_path
        static_path = static_path.rstrip("/") or "/"

        index_name = os.getenv("NESTIPY_WEB_STATIC_INDEX", "index.html").strip()
        if not index_name:
            index_name = "index.html"

        fallback_enabled = os.getenv(
            "NESTIPY_WEB_STATIC_FALLBACK", "1"
        ).strip().lower() not in {"0", "false", "no", "off"}

        def _accepts_html(req: Request) -> bool:
            accept = (req.headers.get("accept") or "").lower()
            return "text/html" in accept or "application/xhtml+xml" in accept

        def _resolve_rel_path(req_path: str) -> Optional[str]:
            path = req_path or "/"
            if static_path != "/":
                if not path.startswith(static_path):
                    return None
                rel = path[len(static_path) :].lstrip("/")
            else:
                rel = path.lstrip("/")
            if not rel or rel.endswith("/"):
                return index_name
            return rel

        def _load_manifest() -> dict[str, JsonValue] | None:
            nonlocal manifest_cache, manifest_mtime, manifest_assets_cache
            candidates = [
                os.path.join(static_dir, ".vite", "manifest.json"),
                os.path.join(static_dir, "manifest.json"),
            ]
            for candidate in candidates:
                if not candidate or not os.path.isfile(candidate):
                    continue
                try:
                    mtime = os.path.getmtime(candidate)
                    if manifest_cache is not None and manifest_mtime == mtime:
                        return manifest_cache
                    with open(candidate, "r", encoding="utf-8") as f:
                        manifest_cache = json.load(f)
                    manifest_mtime = mtime
                    manifest_assets_cache = None
                    return manifest_cache
                except Exception:
                    return None
            return None

        def _manifest_assets() -> set[str]:
            nonlocal manifest_assets_cache
            if manifest_assets_cache is not None:
                return manifest_assets_cache
            manifest = _load_manifest()
            assets: set[str] = set()
            if isinstance(manifest, dict):
                for item in manifest.values():
                    if isinstance(item, dict):
                        file = item.get("file")
                        if file:
                            assets.add(str(file))
                        for css in item.get("css", []) or []:
                            assets.add(str(css))
                        for asset in item.get("assets", []) or []:
                            assets.add(str(asset))
            manifest_assets_cache = assets
            return assets

        def _cache_control_for(rel_path: str) -> str | None:
            if not rel_path:
                return None
            filename = os.path.basename(rel_path)
            if filename == index_name or filename.endswith(".html"):
                return "no-cache"
            manifest_assets = _manifest_assets()
            if rel_path in manifest_assets or f"assets/{filename}" in manifest_assets:
                return "public, max-age=31536000, immutable"
            if hash_re.search(filename):
                return "public, max-age=31536000, immutable"
            return "public, max-age=3600"

        async def _try_web_static(
            req: Request, res: Response, allow_fallback: bool
        ) -> bool:
            rel_path = _resolve_rel_path(req.path)
            if rel_path is None:
                return False
            file_path = os.path.realpath(os.path.join(static_dir, rel_path))
            if not file_path.startswith(static_dir):
                return False
            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, index_name)
            if not os.path.isfile(file_path):
                if allow_fallback and fallback_enabled and _accepts_html(req):
                    file_path = os.path.join(static_dir, index_name)
                    rel_path = index_name
                if not os.path.isfile(file_path):
                    return False
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            cache_control = _cache_control_for(rel_path)
            if cache_control:
                res.header("Cache-Control", cache_control)
            async with aiofiles.open(file_path, "rb") as f:
                payload = await f.read()
            res.header("Content-Type", mime_type)
            await res._write(payload)
            return True

        async def web_static_handler(req: Request, res: Response, _next_fn):
            handled = await _try_web_static(req, res, allow_fallback=True)
            if handled:
                return res
            return await res.status(404).send("Not found")

        self._try_handler = _try_web_static
        logger.info("[WEB] Serving static from %s at %s", static_dir, static_path)
        raw_meta = {"raw": True}
        if static_path == "/":
            self._http_adapter.get("/", web_static_handler, raw_meta)
            self._http_adapter.head("/", web_static_handler, raw_meta)
            static_route = self._http_adapter.create_wichard("", name="path")
        else:
            self._http_adapter.get(static_path, web_static_handler, raw_meta)
            self._http_adapter.head(static_path, web_static_handler, raw_meta)
            static_route = self._http_adapter.create_wichard(
                static_path.strip("/"), name="path"
            )
        if not static_route.startswith("/"):
            static_route = "/" + static_route
        self._http_adapter.get(static_route, web_static_handler, raw_meta)
        self._http_adapter.head(static_route, web_static_handler, raw_meta)
        self._static_root = static_dir
        self._static_path = static_path
        self._index_name = index_name
        self._fallback_enabled = fallback_enabled

    async def maybe_handle(
        self, scope: dict, receive: Callable, send_fn: Callable
    ) -> bool:
        """Handle static requests directly when appropriate."""
        if self._try_handler is None:
            return False
        path = scope.get("path") or "/"
        accept = ""
        for key, value in scope.get("headers", []) or []:
            if key.lower() == b"accept":
                accept = value.decode()
                break
        wants_html = "text/html" in accept or "application/xhtml+xml" in accept
        has_extension = "." in os.path.basename(path.rstrip("/"))
        if not (wants_html or has_extension or path == "/"):
            return False
        req = Request(scope, receive, send_fn)
        res = Response(
            template_engine=self._http_adapter.get_state(TemplateKey.MetaEngine)
        )
        handled = await self._try_handler(req, res, allow_fallback=True)
        if not handled:
            return False
        await self._send_response(res, send_fn)
        return True

    def configure_not_found(self, render_not_found: Callable) -> Callable:
        """Return a not-found handler that falls back to index.html when enabled."""
        static_dir = getattr(self, "_static_root", None)
        static_path = getattr(self, "_static_path", "/")
        index_name = getattr(self, "_index_name", "index.html")
        fallback_enabled = bool(getattr(self, "_fallback_enabled", False))
        if not static_dir or not os.path.isdir(static_dir) or not fallback_enabled:
            return render_not_found

        def _accepts_html(req: Request) -> bool:
            accept = (req.headers.get("accept") or "").lower()
            return "text/html" in accept or "application/xhtml+xml" in accept

        async def web_not_found(req: Request, res: Response, _next_fn):
            path = req.path or "/"
            if static_path != "/" and not (
                path == static_path or path.startswith(static_path + "/")
            ):
                return await render_not_found(req, res, _next_fn)
            is_index_request = path in {"/", static_path}
            if not _accepts_html(req) and not is_index_request:
                return await render_not_found(req, res, _next_fn)
            index_path = os.path.realpath(os.path.join(static_dir, index_name))
            if not index_path.startswith(static_dir) or not os.path.isfile(index_path):
                return await render_not_found(req, res, _next_fn)
            async with aiofiles.open(index_path, "rb") as f:
                payload = await f.read()
            res.header("Content-Type", "text/html; charset=utf-8")
            await res._write(payload)
            return res

        return web_not_found

    async def _send_response(self, res: Response, send_fn: Callable) -> None:
        """Write a Response into the ASGI send channel."""
        headers = [
            (k.encode(), v.encode())
            for k, v in typing.cast(set[tuple[str, str]], res.headers())
        ]
        await send_fn(
            {
                "type": "http.response.start",
                "status": res.status_code(),
                "headers": headers,
            }
        )
        if res.is_stream():
            stream_content = typing.cast(
                Callable[[], typing.AsyncIterator[bytes | str]],
                res.stream_content,
            )
            async for chunk in stream_content():
                payload = chunk.encode() if isinstance(chunk, str) else chunk
                await send_fn(
                    {"type": "http.response.body", "body": payload, "more_body": True}
                )
            await send_fn(
                {"type": "http.response.body", "body": b"", "more_body": False}
            )
            return
        payload = res.content() or b""
        await send_fn(
            {"type": "http.response.body", "body": payload, "more_body": False}
        )


__all__ = ["WebStaticHandler"]
