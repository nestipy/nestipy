from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from nestipy.common.logger import DEFAULT_LOG_FORMAT, build_granian_log_dictconfig, logger

if TYPE_CHECKING:
    from nestipy.core.nestipy_application import NestipyApplication


class GranianServerRunner:
    """Launch Granian with Nestipy-specific defaults and web flags."""
    def __init__(self, app: "NestipyApplication") -> None:
        self._app = app

    def serve(self, target: Optional[str] = None, **options) -> None:
        app = self._app
        web_enabled = bool(options.pop("web", False))
        web_dist = options.pop("web_dist", None)
        web_static_path = options.pop("web_static_path", None)
        web_index = options.pop("web_index", None)
        web_fallback = options.pop("web_fallback", None)

        argv = sys.argv[1:]
        if "--web" in argv:
            web_enabled = True

        def _cli_value(flag: str) -> Optional[str]:
            for idx, arg in enumerate(argv):
                if arg == flag and idx + 1 < len(argv):
                    return argv[idx + 1]
                if arg.startswith(flag + "="):
                    return arg.split("=", 1)[1]
            return None

        if not web_dist:
            web_dist = _cli_value("--web-dist")
        if not web_static_path:
            web_static_path = _cli_value("--web-path")
        if not web_index:
            web_index = _cli_value("--web-index")
        if web_fallback is None:
            web_fallback = _cli_value("--web-fallback")
        web_ssr = "--ssr" in argv or "--web-ssr" in argv
        web_ssr_runtime = _cli_value("--ssr-runtime") or _cli_value("--web-ssr-runtime")
        web_ssr_entry = _cli_value("--ssr-entry") or _cli_value("--web-ssr-entry")

        def _default_web_dist() -> str:
            candidates = ("web/dist", "src/dist", "dist")
            for candidate in candidates:
                if os.path.isdir(candidate):
                    return candidate
            return "web/dist"

        if web_enabled:
            dist = (
                str(web_dist)
                if web_dist
                else os.getenv("NESTIPY_WEB_DIST")
                or _default_web_dist()
            )
            os.environ["NESTIPY_WEB_DIST"] = dist
            logger.info("[WEB] Enabled (dist=%s)", dist)
            if web_static_path:
                os.environ["NESTIPY_WEB_STATIC_PATH"] = str(web_static_path)
            if web_index:
                os.environ["NESTIPY_WEB_STATIC_INDEX"] = str(web_index)
            if web_fallback is not None:
                val = str(web_fallback).strip().lower()
                if val in {"0", "false", "no", "off"}:
                    os.environ["NESTIPY_WEB_STATIC_FALLBACK"] = "0"
                elif val in {"1", "true", "yes", "on"}:
                    os.environ["NESTIPY_WEB_STATIC_FALLBACK"] = "1"
            if web_ssr:
                os.environ["NESTIPY_WEB_SSR"] = "1"
            if web_ssr_runtime:
                os.environ["NESTIPY_WEB_SSR_RUNTIME"] = str(web_ssr_runtime)
            if web_ssr_entry:
                os.environ["NESTIPY_WEB_SSR_ENTRY"] = str(web_ssr_entry)

        if "interface" not in options:
            try:
                from granian.constants import Interfaces as GranianInterfaces

                options["interface"] = GranianInterfaces.ASGI
            except Exception:
                pass
        if "log_dictconfig" not in options:
            options["log_dictconfig"] = getattr(app, "_granian_log_dictconfig", None) or build_granian_log_dictconfig(
                level=getattr(app, "_log_level", None),
                fmt=getattr(app, "_log_format", None) or DEFAULT_LOG_FORMAT,
                datefmt=getattr(app, "_log_datefmt", None),
                use_color=getattr(app, "_log_color", True),
            )
        if "log_access" not in options and getattr(app, "_granian_log_access", None) is not None:
            options["log_access"] = getattr(app, "_granian_log_access")
        if (
            "log_access_format" not in options
            and getattr(app, "_granian_log_access_format", None) is not None
        ):
            options["log_access_format"] = getattr(app, "_granian_log_access_format")
        if options.get("reload") and "reload_ignore_patterns" not in options:
            # Default: reload only for .py changes (ignore other extensions).
            # Keep directories visible to avoid skipping python packages.
            options["reload_ignore_patterns"] = [r".*\.(?!py$)[^/]+$"]
        if options.get("reload"):
            if "reload_paths" not in options:
                env_paths = os.getenv("NESTIPY_RELOAD_PATHS")
                if env_paths:
                    options["reload_paths"] = [
                        Path(p.strip()).expanduser()
                        for p in env_paths.split(",")
                        if p.strip()
                    ]
            if "reload_ignore_paths" not in options:
                env_ignore = os.getenv("NESTIPY_RELOAD_IGNORE_PATHS")
                if env_ignore:
                    options["reload_ignore_paths"] = [
                        Path(p.strip()).expanduser()
                        for p in env_ignore.split(",")
                        if p.strip()
                    ]

        if target is None:
            unsupported = set(options.keys()) - {
                "host",
                "port",
                "uds",
                "interface",
                "blocking_threads",
                "blocking_threads_idle_timeout",
                "runtime_threads",
                "runtime_blocking_threads",
                "task_impl",
                "http",
                "websockets",
                "backlog",
                "backpressure",
                "http1_settings",
                "http2_settings",
                "log_enabled",
                "log_level",
                "log_dictconfig",
                "log_access",
                "log_access_format",
                "ssl_cert",
                "ssl_key",
                "ssl_key_password",
                "ssl_protocol_min",
                "ssl_ca",
                "ssl_crl",
                "ssl_client_verify",
                "url_path_prefix",
                "factory",
                "static_path_route",
                "static_path_mount",
                "static_path_dir_to_file",
                "static_path_expires",
            }
            if unsupported:
                raise ValueError(
                    "Granian embed mode doesn't support options: "
                    + ", ".join(sorted(unsupported))
                    + ". Provide target='main:app' to use full Granian options."
                )
            from granian.server.embed import Server as GranianServer

            server = GranianServer(target=app, **options)
            server.serve()
            return

        from granian import Granian

        server = Granian(target=target, **options, address=options.get("host", None))
        server.serve()


__all__ = ["GranianServerRunner"]
