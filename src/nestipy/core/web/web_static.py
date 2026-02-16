from __future__ import annotations

import collections
import json
import mimetypes
import os
import sys
import time
import typing
from typing import Any, Callable, Optional

import aiofiles

from nestipy.common.http_ import Request, Response
from nestipy.common.logger import logger
from nestipy.common.template import TemplateKey
from nestipy.web.ssr import (
    SSRRenderError,
    create_ssr_renderer,
    env_ssr_enabled,
    env_ssr_runtime,
    resolve_ssr_entry,
)


class WebStaticHandler:
    """Serve built web assets (and optional SSR) before adapter routing."""
    def __init__(
        self,
        http_adapter: Any,
        *,
        on_ssr_renderer: Optional[Callable[[Optional[object]], None]] = None,
    ) -> None:
        self._http_adapter = http_adapter
        self._on_ssr_renderer = on_ssr_renderer
        self._try_handler: Optional[Callable[[Request, Response, bool], typing.Awaitable[bool]]] = None
        self._ssr_renderer: Optional[object] = None

    def register(self) -> None:
        """Register static/SSR handlers on the HTTP adapter."""
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
                "[WEB] Static dist directory not found: %s (run `nestipy run web:build --vite`)",
                static_dir,
            )
            return

        ssr_enabled = env_ssr_enabled()
        ssr_renderer: Optional[object] = None
        ssr_cache_size = int(os.getenv("NESTIPY_WEB_SSR_CACHE", "0") or 0)
        ssr_cache_ttl = float(os.getenv("NESTIPY_WEB_SSR_CACHE_TTL", "0") or 0)
        ssr_cache: "collections.OrderedDict[str, tuple[float, str]]" = collections.OrderedDict()
        ssr_stream = os.getenv("NESTIPY_WEB_SSR_STREAM", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        ssr_manifest_path = os.getenv("NESTIPY_WEB_SSR_MANIFEST")
        manifest_cache: dict[str, Any] | None = None
        manifest_mtime: float | None = None
        manifest_tags_cache: str | None = None
        ssr_allow_routes: list[str] = []
        ssr_deny_routes: list[str] = []
        ssr_routes_loaded = False
        if ssr_enabled:
            runtime = env_ssr_runtime()
            entry_path = os.getenv("NESTIPY_WEB_SSR_ENTRY") or resolve_ssr_entry(static_dir)
            try:
                ssr_renderer = create_ssr_renderer(runtime, entry_path)
                self._ssr_renderer = ssr_renderer
                if self._on_ssr_renderer:
                    self._on_ssr_renderer(ssr_renderer)
                logger.info("[WEB] SSR enabled (runtime=%s)", runtime)
            except ImportError as exc:
                logger.warning("[WEB] SSR disabled (%s)", exc)
            except Exception as exc:
                logger.warning("[WEB] SSR init failed (%s)", exc)

        static_path = os.getenv("NESTIPY_WEB_STATIC_PATH", "/").strip()
        if not static_path:
            static_path = "/"
        if not static_path.startswith("/"):
            static_path = "/" + static_path
        static_path = static_path.rstrip("/") or "/"

        index_name = os.getenv("NESTIPY_WEB_STATIC_INDEX", "index.html").strip()
        if not index_name:
            index_name = "index.html"

        fallback_enabled = (
            os.getenv("NESTIPY_WEB_STATIC_FALLBACK", "1").strip().lower()
            not in {"0", "false", "no", "off"}
        )

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

        def _load_manifest() -> dict[str, Any] | None:
            nonlocal manifest_cache, manifest_mtime, manifest_tags_cache
            candidates = [
                ssr_manifest_path,
                os.path.join(static_dir, ".vite", "ssr-manifest.json"),
                os.path.join(static_dir, ".vite", "manifest.json"),
                os.path.join(static_dir, "manifest.json"),
            ]
            for candidate in candidates:
                if not candidate:
                    continue
                if not os.path.isfile(candidate):
                    continue
                try:
                    mtime = os.path.getmtime(candidate)
                    if manifest_cache is not None and manifest_mtime == mtime:
                        return manifest_cache
                    with open(candidate, "r", encoding="utf-8") as f:
                        manifest_cache = json.load(f)
                    manifest_mtime = mtime
                    manifest_tags_cache = None
                    return manifest_cache
                except Exception:
                    return None
            return None

        def _load_ssr_routes() -> None:
            nonlocal ssr_routes_loaded
            if ssr_routes_loaded:
                return
            ssr_routes_loaded = True
            allow_env = os.getenv("NESTIPY_WEB_SSR_ROUTES", "").strip()
            deny_env = os.getenv("NESTIPY_WEB_SSR_EXCLUDE", "").strip()
            if allow_env:
                ssr_allow_routes.extend([p.strip() for p in allow_env.split(",") if p.strip()])
            if deny_env:
                ssr_deny_routes.extend([p.strip() for p in deny_env.split(",") if p.strip()])
            if ssr_allow_routes or ssr_deny_routes:
                return
            route_path = os.path.join(static_dir, "ssr-routes.json")
            if not os.path.isfile(route_path):
                return
            try:
                with open(route_path, "r", encoding="utf-8") as f:
                    payload = json.load(f)
            except Exception:
                return
            for entry in payload.get("routes", []):
                path = entry.get("path")
                if not path:
                    continue
                if entry.get("ssr") is False:
                    ssr_deny_routes.append(path)
                else:
                    ssr_allow_routes.append(path)

        def _match_route(pattern: str, path: str) -> bool:
            if not pattern:
                return False
            if pattern == "/":
                return path == "/" or path == ""
            pat = pattern.strip("/")
            target = path.strip("/")
            if not pat:
                return target == ""
            pat_parts = pat.split("/")
            tgt_parts = target.split("/") if target else []
            idx = 0
            for part in pat_parts:
                if part == "*":
                    return True
                if idx >= len(tgt_parts):
                    return False
                if part.startswith(":"):
                    idx += 1
                    continue
                if part != tgt_parts[idx]:
                    return False
                idx += 1
            return idx == len(tgt_parts)

        def _should_ssr(path: str) -> bool:
            _load_ssr_routes()
            if ssr_allow_routes:
                return any(_match_route(pattern, path) for pattern in ssr_allow_routes)
            if ssr_deny_routes:
                return not any(_match_route(pattern, path) for pattern in ssr_deny_routes)
            return True

        def _build_manifest_tags() -> str:
            nonlocal manifest_tags_cache
            if manifest_tags_cache is not None:
                return manifest_tags_cache
            manifest = _load_manifest()
            if not isinstance(manifest, dict):
                manifest_tags_cache = ""
                return manifest_tags_cache
            entry = manifest.get("src/entry-client.tsx") or manifest.get("src/main.tsx")
            if not isinstance(entry, dict):
                manifest_tags_cache = ""
                return manifest_tags_cache
            links: list[str] = []
            seen: set[str] = set()

            def _add_link(tag: str) -> None:
                if tag in seen:
                    return
                seen.add(tag)
                links.append(tag)

            for css in entry.get("css", []) or []:
                _add_link(f"<link rel=\"stylesheet\" href=\"/{css}\">")
            file = entry.get("file")
            if file:
                _add_link(f"<link rel=\"modulepreload\" href=\"/{file}\">")
            for imp in entry.get("imports", []) or []:
                target = manifest.get(imp)
                if isinstance(target, dict):
                    imp_file = target.get("file")
                    if imp_file:
                        _add_link(f"<link rel=\"modulepreload\" href=\"/{imp_file}\">")
            manifest_tags_cache = "\n".join(links)
            return manifest_tags_cache

        def _render_ssr_payload(html: str) -> str:
            index_file = os.path.join(static_dir, index_name)
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    template = f.read()
            except Exception:
                return html
            marker = "<div id=\"root\"></div>"
            if marker in template:
                template = template.replace(marker, f"<div id=\"root\">{html}</div>")
            tags = _build_manifest_tags()
            if tags and "</head>" in template:
                template = template.replace("</head>", f"{tags}\n</head>")
            return template

        async def _try_web_static(req: Request, res: Response, allow_fallback: bool) -> bool:
            rel_path = _resolve_rel_path(req.path)
            if rel_path is None:
                return False
            if ssr_renderer is not None and _accepts_html(req):
                try:
                    query = req.scope.get("query_string") or b""
                    qs = query.decode() if isinstance(query, (bytes, bytearray)) else str(query)
                    route_path = req.path or "/"
                    if static_path != "/" and route_path.startswith(static_path):
                        route_path = route_path[len(static_path) :] or "/"
                    if not _should_ssr(route_path):
                        raise SSRRenderError("SSR disabled for route")
                    url = route_path + (f"?{qs}" if qs else "")
                    if ssr_cache_size > 0:
                        cached = ssr_cache.get(url)
                        if cached:
                            ts, payload = cached
                            if ssr_cache_ttl <= 0 or (time.time() - ts) <= ssr_cache_ttl:
                                await res.header("Content-Type", "text/html").send(payload)
                                return True
                            ssr_cache.pop(url, None)
                    rendered = await typing.cast(Any, ssr_renderer).render(url)
                    if rendered:
                        payload = _render_ssr_payload(rendered)
                        if ssr_cache_size > 0:
                            ssr_cache[url] = (time.time(), payload)
                            while len(ssr_cache) > ssr_cache_size:
                                ssr_cache.popitem(last=False)
                        if ssr_stream:
                            res.header("Content-Type", "text/html")

                            async def _stream():
                                yield payload

                            await res.stream(_stream)
                            return True
                        await res.header("Content-Type", "text/html").send(payload)
                        return True
                except SSRRenderError as exc:
                    message = str(exc)
                    if "disabled for route" not in message.lower():
                        logger.warning("[WEB] SSR render failed (%s)", exc)
                except Exception:
                    logger.exception("[WEB] SSR render crashed")
            file_path = os.path.realpath(os.path.join(static_dir, rel_path))
            if not file_path.startswith(static_dir):
                return False
            if os.path.isdir(file_path):
                file_path = os.path.join(file_path, index_name)
            if not os.path.isfile(file_path):
                if allow_fallback and fallback_enabled and _accepts_html(req):
                    file_path = os.path.join(static_dir, index_name)
                if not os.path.isfile(file_path):
                    return False
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
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

    async def maybe_handle(self, scope: dict, receive: Callable, send_fn: Callable) -> bool:
        """Handle static/SSR requests directly when appropriate."""
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
        res = Response(template_engine=self._http_adapter.get_state(TemplateKey.MetaEngine))
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
            {"type": "http.response.start", "status": res.status_code(), "headers": headers}
        )
        if res.is_stream():
            async for chunk in typing.cast(Any, res.stream_content)():
                payload = chunk.encode() if isinstance(chunk, str) else chunk
                await send_fn({"type": "http.response.body", "body": payload, "more_body": True})
            await send_fn({"type": "http.response.body", "body": b"", "more_body": False})
            return
        payload = res.content() or b""
        await send_fn({"type": "http.response.body", "body": payload, "more_body": False})


__all__ = ["WebStaticHandler"]
