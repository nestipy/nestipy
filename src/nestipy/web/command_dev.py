from __future__ import annotations

import os
import shlex
import subprocess
import time
import traceback
from typing import Iterable, Type

from nestipy.common.logger import logger
from nestipy.web.compiler import CompilerError, compile_app
from nestipy.web.config import WebConfig
from nestipy.web.client import codegen_client

from .command_args import parse_args
from .command_build import build_vite
from .command_codegen import (
    maybe_codegen_actions,
    maybe_codegen_actions_schema,
    maybe_codegen_client,
    maybe_codegen_router_spec,
)
from .command_pkg import install_deps
from .command_shell import select_package_manager, web_log


def dev(args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Run the dev loop with optional Vite and backend processes."""
    parsed = parse_args(args)
    proxy = str(parsed.get("proxy") or os.getenv("NESTIPY_WEB_PROXY") or "") or None
    proxy_paths = str(parsed.get("proxy_paths") or os.getenv("NESTIPY_WEB_PROXY_PATHS") or "")
    proxy_paths_list = (
        [p.strip() for p in proxy_paths.split(",") if p.strip()] if proxy_paths else None
    )
    backend_cmd = parsed.get("backend") or os.getenv("NESTIPY_WEB_BACKEND")
    backend_cwd = parsed.get("backend_cwd") or os.getenv("NESTIPY_WEB_BACKEND_CWD")
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
        proxy=proxy,
        proxy_paths=proxy_paths_list or WebConfig().proxy_paths,
    )
    app_dir = config.resolve_app_dir()
    last_state: dict[str, float] = {}
    vite_process: subprocess.Popen[str] | None = None
    backend_process: subprocess.Popen[str] | None = None
    actions_schema_url: str | None = None
    actions_output: str | None = None
    actions_hash: str | None = None
    actions_etag: str | None = None
    actions_poll_interval = float(os.getenv("NESTIPY_WEB_ACTIONS_POLL", "1.0") or 1.0)
    last_actions_poll = 0.0
    actions_watch_paths: list[str] = []
    last_actions_state: dict[str, float] | None = None

    router_spec_url: str | None = None
    router_output: str | None = None
    router_poll_interval = float(os.getenv("NESTIPY_WEB_ROUTER_POLL", "2.0") or 2.0)
    last_router_poll = 0.0
    router_hash: str | None = None

    if parsed.get("actions"):
        spec_url = parsed.get("spec")
        if spec_url:
            actions_schema_url = str(spec_url)
        elif config.proxy:
            actions_endpoint = str(parsed.get("actions_endpoint", "/_actions"))
            if not actions_endpoint.startswith("/"):
                actions_endpoint = "/" + actions_endpoint
            actions_schema_url = config.proxy.rstrip("/") + actions_endpoint + "/schema"
        output = parsed.get("actions_output")
        if not output:
            actions_output = str(config.resolve_src_dir() / "actions.client.ts")
        else:
            actions_output = str(output)
        actions_watch = str(
            parsed.get("actions_watch")
            or os.getenv("NESTIPY_WEB_ACTIONS_WATCH", "")
            or ""
        )
        if actions_watch:
            actions_watch_paths = [p.strip() for p in actions_watch.split(",") if p.strip()]
        if actions_watch_paths and "NESTIPY_WEB_ACTIONS_POLL" not in os.environ:
            actions_poll_interval = 0.0

    router_spec_url = (
        str(parsed.get("router_spec") or os.getenv("NESTIPY_WEB_ROUTER_SPEC_URL") or "")
        or None
    )
    if not router_spec_url and os.getenv("NESTIPY_ROUTER_SPEC") and proxy:
        router_spec_url = proxy.rstrip("/") + "/_router/spec"
    router_output = str(
        parsed.get("router_output")
        or os.getenv("NESTIPY_WEB_ROUTER_OUTPUT")
        or config.resolve_src_dir() / "api" / "client.ts"
    )
    if actions_watch_paths and "NESTIPY_WEB_ROUTER_POLL" not in os.environ:
        router_poll_interval = 0.0

    def snapshot() -> dict[str, float]:
        """Capture modification times for app source files."""
        state: dict[str, float] = {}
        for path in app_dir.rglob("*.py"):
            try:
                state[str(path)] = path.stat().st_mtime
            except FileNotFoundError:
                continue
        return state

    def snapshot_actions(paths: list[str]) -> dict[str, float]:
        """Capture modification times for backend action source files."""
        state: dict[str, float] = {}
        for raw in paths:
            base = os.path.abspath(raw)
            if os.path.isfile(base):
                if base.endswith(".py"):
                    try:
                        state[base] = os.path.getmtime(base)
                    except FileNotFoundError:
                        continue
                continue
            for root, _dirs, files in os.walk(base):
                for name in files:
                    if not name.endswith(".py"):
                        continue
                    full = os.path.join(root, name)
                    try:
                        state[full] = os.path.getmtime(full)
                    except FileNotFoundError:
                        continue
        return state

    last_state = snapshot()
    try:
        compile_app(config)
    except CompilerError:
        logger.exception("[WEB] compile failed")
        if not logger.isEnabledFor(20):
            traceback.print_exc()
    if router_spec_url and router_output:
        router_hash = maybe_codegen_router_spec(router_spec_url, router_output, router_hash)
    elif modules is not None:
        client_language = str(parsed.get("lang", "ts"))
        class_name = str(parsed.get("class_name", "ApiClient"))
        prefix = str(parsed.get("prefix", ""))
        codegen_client(
            modules,
            str(router_output),
            language=client_language,
            class_name=class_name,
            prefix=prefix,
        )
    maybe_codegen_client(parsed, config)
    maybe_codegen_actions(parsed, config, modules)
    if actions_schema_url and actions_output:
        if actions_watch_paths:
            last_actions_state = snapshot_actions(actions_watch_paths)
        actions_hash, actions_etag = maybe_codegen_actions_schema(
            actions_schema_url,
            actions_output,
            actions_hash,
            actions_etag,
        )
    if parsed.get("vite"):
        if parsed.get("install"):
            install_deps(config)
        vite_process = start_vite(config)
        if vite_process.stdout is not None:
            def _stream_vite_logs() -> None:
                for raw in iter(vite_process.stdout.readline, ""):
                    line = raw.strip()
                    if line:
                        web_log(line)
                code = vite_process.wait()
                if code != 0:
                    web_log(f"Vite dev server exited (code={code}).")
            import threading

            threading.Thread(target=_stream_vite_logs, daemon=True).start()
        if parsed.get("ssr"):
            web_log("SSR build enabled for dev (will rebuild on changes).")
    if backend_cmd:
        backend_env: dict[str, str] = {}
        if "NESTIPY_RELOAD_IGNORE_PATHS" not in os.environ:
            backend_env["NESTIPY_RELOAD_IGNORE_PATHS"] = str(app_dir)
        backend_process = start_backend(
            str(backend_cmd),
            cwd=str(backend_cwd) if backend_cwd else None,
            env=backend_env,
        )
    try:
        while True:
            time.sleep(0.5)
            current = snapshot()
            if current != last_state:
                try:
                    compile_app(config)
                except CompilerError:
                    logger.exception("[WEB] compile failed")
                    if not logger.isEnabledFor(20):
                        traceback.print_exc()
                if parsed.get("ssr") and parsed.get("vite"):
                    ssr_entry = str(parsed.get("ssr_entry") or "src/entry-server.tsx")
                    ssr_out_dir = str(parsed.get("ssr_out_dir") or "dist/ssr")
                    try:
                        build_vite(
                            config,
                            ssr=True,
                            ssr_entry=ssr_entry,
                            ssr_out_dir=ssr_out_dir,
                        )
                    except Exception:
                        logger.exception("[WEB] SSR build failed")
                        if not logger.isEnabledFor(20):
                            traceback.print_exc()
                maybe_codegen_client(parsed, config)
                maybe_codegen_actions(parsed, config, modules)
                if actions_schema_url and actions_output:
                    if actions_watch_paths:
                        last_actions_state = snapshot_actions(actions_watch_paths)
                    actions_hash, actions_etag = maybe_codegen_actions_schema(
                        actions_schema_url,
                        actions_output,
                        actions_hash,
                        actions_etag,
                    )
                if router_spec_url and router_output:
                    router_hash = maybe_codegen_router_spec(
                        router_spec_url, router_output, router_hash
                    )
                elif modules is not None:
                    client_language = str(parsed.get("lang", "ts"))
                    class_name = str(parsed.get("class_name", "ApiClient"))
                    prefix = str(parsed.get("prefix", ""))
                    codegen_client(
                        modules,
                        str(router_output),
                        language=client_language,
                        class_name=class_name,
                        prefix=prefix,
                    )
                last_state = current
            if actions_schema_url and actions_output and actions_watch_paths:
                current_actions_state = snapshot_actions(actions_watch_paths)
                if current_actions_state != (last_actions_state or {}):
                    actions_hash, actions_etag = maybe_codegen_actions_schema(
                        actions_schema_url,
                        actions_output,
                        actions_hash,
                        actions_etag,
                    )
                    last_actions_state = current_actions_state
                    last_actions_poll = time.monotonic()
                    if router_spec_url and router_output:
                        router_hash = maybe_codegen_router_spec(
                            router_spec_url, router_output, router_hash
                        )
                    elif modules is not None:
                        client_language = str(parsed.get("lang", "ts"))
                        class_name = str(parsed.get("class_name", "ApiClient"))
                        prefix = str(parsed.get("prefix", ""))
                        codegen_client(
                            modules,
                            str(router_output),
                            language=client_language,
                            class_name=class_name,
                            prefix=prefix,
                        )
                    last_router_poll = time.monotonic()
            now = time.monotonic()
            if (
                actions_schema_url
                and actions_output
                and actions_poll_interval > 0.0
                and now - last_actions_poll >= actions_poll_interval
            ):
                actions_hash, actions_etag = maybe_codegen_actions_schema(
                    actions_schema_url,
                    actions_output,
                    actions_hash,
                    actions_etag,
                )
                last_actions_poll = now
            if (
                router_spec_url
                and router_output
                and router_poll_interval > 0.0
                and now - last_router_poll >= router_poll_interval
            ):
                router_hash = maybe_codegen_router_spec(
                    router_spec_url, router_output, router_hash
                )
                last_router_poll = now
    except KeyboardInterrupt:
        if vite_process is not None:
            vite_process.terminate()
        if backend_process is not None:
            backend_process.terminate()
        return


def start_vite(config: WebConfig) -> subprocess.Popen[str]:
    """Start the Vite dev server using the detected package manager."""
    out_dir = config.resolve_out_dir()
    manager = select_package_manager(out_dir)
    if manager == "pnpm":
        cmd = ["pnpm", "dev"]
    elif manager == "yarn":
        cmd = ["yarn", "dev"]
    else:
        cmd = ["npm", "run", "dev"]
    return subprocess.Popen(
        cmd,
        cwd=str(out_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def start_backend(
    command: str,
    cwd: str | None = None,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.Popen[str]:
    """Start the backend process from a shell command."""
    cmd = shlex.split(command)
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.Popen(cmd, cwd=cwd, env=merged_env)
