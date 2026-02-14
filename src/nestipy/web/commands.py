from __future__ import annotations

import os
import time
import shlex
import subprocess
import json
import hashlib
import urllib.request
import urllib.error
import traceback
from typing import Iterable, Type

from nestipy.common.logger import logger
from nestipy.web.config import WebConfig
from nestipy.web.compiler import compile_app, CompilerError
from nestipy.web.client import codegen_client, codegen_client_from_url
from nestipy.web.actions_client import (
    write_actions_client_file,
    codegen_actions_from_url,
    generate_actions_client_code_from_schema,
)


def _parse_args(args: Iterable[str]) -> dict[str, str | bool]:
    """Parse Nestipy web CLI arguments into a simple dict."""
    parsed: dict[str, str | bool] = {}
    args_list = list(args)
    i = 0
    while i < len(args_list):
        arg = args_list[i]
        if arg in {"--app", "--app-dir"} and i + 1 < len(args_list):
            parsed["app_dir"] = args_list[i + 1]
            i += 1
        elif arg in {"--out", "--out-dir"} and i + 1 < len(args_list):
            parsed["out_dir"] = args_list[i + 1]
            i += 1
        elif arg == "--clean":
            parsed["clean"] = True
        elif arg == "--watch":
            parsed["watch"] = True
        elif arg == "--vite":
            parsed["vite"] = True
        elif arg == "--install":
            parsed["install"] = True
        elif arg == "--backend" and i + 1 < len(args_list):
            parsed["backend"] = args_list[i + 1]
            i += 1
        elif arg == "--backend-cwd" and i + 1 < len(args_list):
            parsed["backend_cwd"] = args_list[i + 1]
            i += 1
        elif arg == "--proxy" and i + 1 < len(args_list):
            parsed["proxy"] = args_list[i + 1]
            i += 1
        elif arg == "--proxy-paths" and i + 1 < len(args_list):
            parsed["proxy_paths"] = args_list[i + 1]
            i += 1
        elif arg == "--router-spec" and i + 1 < len(args_list):
            parsed["router_spec"] = args_list[i + 1]
            i += 1
        elif arg == "--router-output" and i + 1 < len(args_list):
            parsed["router_output"] = args_list[i + 1]
            i += 1
        elif arg == "--no-build":
            parsed["no_build"] = True
        elif arg in {"--dev", "-D"}:
            parsed["dev"] = True
        elif arg == "--peer":
            parsed["peer"] = True
        elif arg == "--actions":
            parsed["actions"] = True
        elif arg == "--actions-output" and i + 1 < len(args_list):
            parsed["actions_output"] = args_list[i + 1]
            i += 1
        elif arg == "--actions-endpoint" and i + 1 < len(args_list):
            parsed["actions_endpoint"] = args_list[i + 1]
            i += 1
        elif arg == "--actions-watch" and i + 1 < len(args_list):
            parsed["actions_watch"] = args_list[i + 1]
            i += 1
        elif arg == "--ssr":
            parsed["ssr"] = True
        elif arg == "--ssr-entry" and i + 1 < len(args_list):
            parsed["ssr_entry"] = args_list[i + 1]
            i += 1
        elif arg == "--ssr-out-dir" and i + 1 < len(args_list):
            parsed["ssr_out_dir"] = args_list[i + 1]
            i += 1
        elif arg == "--ssr-runtime" and i + 1 < len(args_list):
            parsed["ssr_runtime"] = args_list[i + 1]
            i += 1
        elif arg == "--target" and i + 1 < len(args_list):
            parsed["target"] = args_list[i + 1]
            i += 1
        elif arg == "--spec" and i + 1 < len(args_list):
            parsed["spec"] = args_list[i + 1]
            i += 1
        elif arg == "--output" and i + 1 < len(args_list):
            parsed["output"] = args_list[i + 1]
            i += 1
        elif arg == "--lang" and i + 1 < len(args_list):
            parsed["lang"] = args_list[i + 1]
            i += 1
        elif arg == "--class" and i + 1 < len(args_list):
            parsed["class_name"] = args_list[i + 1]
            i += 1
        elif arg == "--prefix" and i + 1 < len(args_list):
            parsed["prefix"] = args_list[i + 1]
            i += 1
        i += 1
    return parsed


def _collect_packages(args: Iterable[str]) -> list[str]:
    """Extract non-flag arguments as package specs."""
    args_list = list(args)
    packages: list[str] = []
    skip_next = False
    flags_with_values = {
        "--app",
        "--app-dir",
        "--out",
        "--out-dir",
        "--backend",
        "--backend-cwd",
        "--proxy",
        "--proxy-paths",
        "--actions-output",
        "--actions-endpoint",
        "--actions-watch",
        "--ssr-entry",
        "--ssr-out-dir",
        "--ssr-runtime",
        "--target",
        "--spec",
        "--output",
        "--lang",
        "--class",
        "--prefix",
    }
    flags_bool = {
        "--clean",
        "--watch",
        "--vite",
        "--install",
        "--no-build",
        "--actions",
        "--ssr",
        "--dev",
        "-D",
        "--peer",
    }
    for arg in args_list:
        if skip_next:
            skip_next = False
            continue
        if arg in flags_with_values:
            skip_next = True
            continue
        if arg in flags_bool:
            continue
        if arg.startswith("--"):
            continue
        packages.append(arg)
    return packages


def build(args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Build the frontend and optionally generate clients."""
    parsed = _parse_args(args)
    proxy = str(parsed.get("proxy") or os.getenv("NESTIPY_WEB_PROXY") or "") or None
    proxy_paths = str(parsed.get("proxy_paths") or os.getenv("NESTIPY_WEB_PROXY_PATHS") or "")
    proxy_paths_list = (
        [p.strip() for p in proxy_paths.split(",") if p.strip()] if proxy_paths else None
    )
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
        proxy=proxy,
        proxy_paths=proxy_paths_list or WebConfig().proxy_paths,
    )
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
            _build_vite(config, ssr=True, ssr_entry=ssr_entry, ssr_out_dir=ssr_out_dir)
        except Exception:
            logger.exception("[WEB] SSR build failed")
            if not logger.isEnabledFor(20):
                traceback.print_exc()
        raise
    if modules is not None:
        actions_output = parsed.get("actions_output")
        if not actions_output:
            actions_output = str(config.resolve_src_dir() / "actions.client.ts")
        actions_endpoint = str(parsed.get("actions_endpoint", "/_actions"))
        write_actions_client_file(modules, str(actions_output), endpoint=actions_endpoint)

        client_output = parsed.get("output")
        if not client_output:
            client_output = str(config.resolve_src_dir() / "api" / "client.ts")
        client_language = str(parsed.get("lang", "ts"))
        class_name = str(parsed.get("class_name", "ApiClient"))
        prefix = str(parsed.get("prefix", ""))
        codegen_client(
            modules,
            str(client_output),
            language=client_language,
            class_name=class_name,
            prefix=prefix,
        )
    else:
        _maybe_codegen_client(parsed, config)
        _maybe_codegen_actions(parsed, config, modules)
    if parsed.get("vite"):
        from nestipy.web.compiler import ensure_vite_files

        ensure_vite_files(config)
        if parsed.get("install"):
            _install_deps(config)
        ssr_enabled = bool(parsed.get("ssr"))
        ssr_entry = str(parsed.get("ssr_entry") or "src/entry-server.tsx")
        ssr_out_dir = str(parsed.get("ssr_out_dir") or "dist/ssr")
        _build_vite(config, ssr=ssr_enabled, ssr_entry=ssr_entry, ssr_out_dir=ssr_out_dir)


def init(args: Iterable[str]) -> None:
    """Scaffold a minimal Nestipy Web app."""
    parsed = _parse_args(args)
    proxy = str(parsed.get("proxy") or os.getenv("NESTIPY_WEB_PROXY") or "") or None
    proxy_paths = str(parsed.get("proxy_paths") or os.getenv("NESTIPY_WEB_PROXY_PATHS") or "")
    proxy_paths_list = (
        [p.strip() for p in proxy_paths.split(",") if p.strip()] if proxy_paths else None
    )
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
        proxy=proxy,
        proxy_paths=proxy_paths_list or WebConfig().proxy_paths,
    )
    app_dir = config.resolve_app_dir()
    app_dir.mkdir(parents=True, exist_ok=True)

    page_file = app_dir / "page.py"
    if not page_file.exists():
        page_file.write_text(
            "\n".join(
                [
                    "from nestipy.web import component, h",
                    "",
                    "@component",
                    "def Page():",
                    "    return h.div(",
                    "        h.h1(\"Nestipy Web\"),",
                    "        h.p(\"Edit app/page.py to get started.\"),",
                    "        class_name=\"p-8 space-y-2\",",
                    "    )",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    layout_file = app_dir / "layout.py"
    if not layout_file.exists():
        layout_file.write_text(
            "\n".join(
                [
                    "from nestipy.web import component, h, Slot",
                    "",
                    "@component",
                    "def Layout():",
                    "    return h.div(",
                    "        h.header(\"Nestipy Web\", class_name=\"text-xl font-semibold\"),",
                    "        h(Slot),",
                    "        class_name=\"min-h-screen bg-slate-950 text-white p-8 space-y-6\",",
                    "    )",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    actions_file = app_dir / "actions.py"
    if not actions_file.exists():
        actions_file.write_text(
            "\n".join(
                [
                    "from nestipy.web import action",
                    "",
                    "class DemoActions:",
                    "    @action()",
                    "    async def hello(self, name: str = \"world\") -> str:",
                    "        return f\"Hello, {name}!\"",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    if not parsed.get("no_build"):
        try:
            compile_app(config)
        except CompilerError:
            logger.exception("[WEB] compile failed")
            if not logger.isEnabledFor(20):
                traceback.print_exc()
            raise


def dev(args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Run the dev loop with optional Vite and backend processes."""
    parsed = _parse_args(args)
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
        router_hash = _maybe_codegen_router_spec(router_spec_url, router_output, router_hash)
    _maybe_codegen_client(parsed, config)
    _maybe_codegen_actions(parsed, config, modules)
    if actions_schema_url and actions_output:
        if actions_watch_paths:
            last_actions_state = snapshot_actions(actions_watch_paths)
        actions_hash, actions_etag = _maybe_codegen_actions_schema(
            actions_schema_url,
            actions_output,
            actions_hash,
            actions_etag,
        )
    if parsed.get("vite"):
        if parsed.get("install"):
            _install_deps(config)
        vite_process = _start_vite(config)
        if parsed.get("ssr"):
            _web_log("SSR build enabled for dev (will rebuild on changes).")
    if backend_cmd:
        backend_env: dict[str, str] = {}
        if "NESTIPY_RELOAD_IGNORE_PATHS" not in os.environ:
            backend_env["NESTIPY_RELOAD_IGNORE_PATHS"] = str(app_dir)
        backend_process = _start_backend(
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
                        _build_vite(
                            config,
                            ssr=True,
                            ssr_entry=ssr_entry,
                            ssr_out_dir=ssr_out_dir,
                        )
                    except Exception:
                        logger.exception("[WEB] SSR build failed")
                        if not logger.isEnabledFor(20):
                            traceback.print_exc()
                _maybe_codegen_client(parsed, config)
                _maybe_codegen_actions(parsed, config, modules)
                if actions_schema_url and actions_output:
                    if actions_watch_paths:
                        last_actions_state = snapshot_actions(actions_watch_paths)
                    actions_hash, actions_etag = _maybe_codegen_actions_schema(
                        actions_schema_url,
                        actions_output,
                        actions_hash,
                        actions_etag,
                    )
                if router_spec_url and router_output:
                    router_hash = _maybe_codegen_router_spec(
                        router_spec_url, router_output, router_hash
                    )
                last_state = current
            if actions_schema_url and actions_output and actions_watch_paths:
                current_actions_state = snapshot_actions(actions_watch_paths)
                if current_actions_state != (last_actions_state or {}):
                    actions_hash, actions_etag = _maybe_codegen_actions_schema(
                        actions_schema_url,
                        actions_output,
                        actions_hash,
                        actions_etag,
                    )
                    last_actions_state = current_actions_state
                    last_actions_poll = time.monotonic()
                    if router_spec_url and router_output:
                        router_hash = _maybe_codegen_router_spec(
                            router_spec_url, router_output, router_hash
                        )
                    last_router_poll = time.monotonic()
            now = time.monotonic()
            if (
                actions_schema_url
                and actions_output
                and actions_poll_interval > 0.0
                and now - last_actions_poll >= actions_poll_interval
            ):
                actions_hash, actions_etag = _maybe_codegen_actions_schema(
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
                router_hash = _maybe_codegen_router_spec(
                    router_spec_url, router_output, router_hash
                )
                last_router_poll = now
    except KeyboardInterrupt:
        if vite_process is not None:
            vite_process.terminate()
        if backend_process is not None:
            backend_process.terminate()
        return


def codegen(args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Generate an API client from a router spec or modules."""
    parsed = _parse_args(args)
    output = parsed.get("output")
    if not output:
        raise RuntimeError("Missing --output for web:codegen")

    language = str(parsed.get("lang", "python"))
    class_name = str(parsed.get("class_name", "ApiClient"))
    prefix = str(parsed.get("prefix", ""))

    spec_url = parsed.get("spec")
    if spec_url:
        codegen_client_from_url(str(spec_url), str(output), language=language, class_name=class_name)
        return

    if modules is None:
        raise RuntimeError("Modules are required to generate client without --spec")

    codegen_client(modules, str(output), language=language, class_name=class_name, prefix=prefix)


def run_command(command_name: str, args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Dispatch the web subcommand by name."""
    if command_name == "web:init":
        init(args)
    elif command_name == "web:build":
        build(args, modules=modules)
    elif command_name == "web:dev":
        dev(args, modules=modules)
    elif command_name == "web:install":
        install(args)
    elif command_name == "web:add":
        add(args)
    elif command_name == "web:codegen":
        codegen(args, modules=modules)
    elif command_name == "web:actions":
        codegen_actions(args, modules=modules)
    else:
        raise RuntimeError(f"Unknown web command: {command_name}")


def _maybe_codegen_client(parsed: dict[str, str | bool], config: WebConfig) -> None:
    """Generate a router client if a spec URL is configured."""
    spec_url = parsed.get("spec")
    if not spec_url:
        return
    language = str(parsed.get("lang", "ts"))
    output = parsed.get("output")
    if not output:
        default_path = config.resolve_src_dir() / "api" / "client.ts"
        output = str(default_path)
    class_name = str(parsed.get("class_name", "ApiClient"))
    codegen_client_from_url(str(spec_url), str(output), language=language, class_name=class_name)


def codegen_actions(args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Generate an actions client from modules or a schema URL."""
    parsed = _parse_args(args)
    spec_url = parsed.get("spec")
    if modules is None:
        if spec_url:
            output = parsed.get("actions_output") or parsed.get("output")
            if not output:
                output = "web/src/actions.client.ts"
            codegen_actions_from_url(str(spec_url), str(output))
            return
        raise RuntimeError("Modules are required to generate actions client")
    output = parsed.get("actions_output") or parsed.get("output")
    if not output:
        output = "web/src/actions.client.ts"
    endpoint = str(parsed.get("actions_endpoint", "/_actions"))
    write_actions_client_file(modules, str(output), endpoint=endpoint)


def _maybe_codegen_actions(
    parsed: dict[str, str | bool], config: WebConfig, modules: list[Type] | None
) -> None:
    """Generate an actions client if requested via CLI flags."""
    if not parsed.get("actions"):
        return
    spec_url = parsed.get("spec")
    output = parsed.get("actions_output")
    if not output:
        output = str(config.resolve_src_dir() / "actions.client.ts")
    if modules is None:
        if spec_url:
            codegen_actions_from_url(str(spec_url), str(output))
        return
    endpoint = str(parsed.get("actions_endpoint", "/_actions"))
    write_actions_client_file(modules, str(output), endpoint=endpoint)


def _maybe_codegen_actions_schema(
    url: str,
    output: str,
    last_hash: str | None,
    last_etag: str | None,
) -> tuple[str | None, str | None]:
    """Fetch the action schema and update the client file if it changed."""
    headers: dict[str, str] = {}
    if last_etag:
        headers["If-None-Match"] = last_etag
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            etag = response.headers.get("ETag")
            schema = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            return last_hash, last_etag
        return last_hash, last_etag
    except Exception:
        return last_hash, last_etag
    code = generate_actions_client_code_from_schema(schema)
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()
    if digest == last_hash:
        return last_hash, last_etag
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        f.write(code)
    logger.info("[WEB] Actions client updated")
    return digest, (etag or last_etag)


def _hash_file(path: str) -> str | None:
    """Hash a file's content for change detection."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def _maybe_codegen_router_spec(
    url: str,
    output: str,
    last_hash: str | None,
) -> str | None:
    """Fetch the router spec and update the client file if it changed."""
    try:
        codegen_client_from_url(url, output, language="ts", class_name="ApiClient")
    except Exception:
        logger.exception("[WEB] router client generation failed")
        if not logger.isEnabledFor(20):
            traceback.print_exc()
        return last_hash
    digest = _hash_file(output)
    if digest and digest != last_hash:
        logger.info("[WEB] API client updated")
    return digest or last_hash


def _start_vite(config: WebConfig) -> subprocess.Popen[str]:
    """Start the Vite dev server using the detected package manager."""
    out_dir = config.resolve_out_dir()
    manager = _select_package_manager(out_dir)
    if manager == "pnpm":
        cmd = ["pnpm", "dev"]
    elif manager == "yarn":
        cmd = ["yarn", "dev"]
    else:
        cmd = ["npm", "run", "dev"]
    return subprocess.Popen(cmd, cwd=str(out_dir))


def _web_build_log_mode() -> str:
    mode = os.getenv("NESTIPY_WEB_BUILD_LOG", "summary").strip().lower()
    if mode not in {"summary", "verbose", "silent"}:
        mode = "summary"
    return mode


def _web_log(message: str) -> None:
    if logger.isEnabledFor(20):
        logger.info("[WEB] %s", message)
    else:
        print(f"[NESTIPY] INFO [WEB] {message}")


def _run_command_capture(cmd: list[str], cwd: str) -> tuple[int, list[str]]:
    lines: list[str] = []
    process = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )
    assert process.stdout is not None
    for raw in process.stdout:
        line = raw.rstrip("\n")
        if line:
            lines.append(line)
        if _web_build_log_mode() == "verbose":
            _web_log(line)
    return process.wait(), lines


def _summarize_build_lines(lines: list[str]) -> None:
    mode = _web_build_log_mode()
    if mode == "silent":
        return
    for line in lines:
        text = line.strip()
        lower = text.lower()
        if text.startswith("dist/") or text.startswith("web/dist/"):
            _web_log(text)
        elif "building" in lower and "vite" in lower:
            _web_log(text)
        elif "modules transformed" in lower:
            _web_log(text)
        elif "built in" in lower:
            _web_log(text)


def _build_vite(
    config: WebConfig,
    *,
    ssr: bool = False,
    ssr_entry: str = "src/entry-server.tsx",
    ssr_out_dir: str = "dist/ssr",
) -> None:
    """Run the Vite production build using the detected package manager."""
    out_dir = config.resolve_out_dir()
    manager = _select_package_manager(out_dir)

    def build_cmd(extra: list[str]) -> list[str]:
        args = ["--", *extra] if extra else []
        if manager == "pnpm":
            return ["pnpm", "build", *args]
        if manager == "yarn":
            return ["yarn", "build", *args]
        return ["npm", "run", "build", *args]

    if ssr:
        rc, lines = _run_command_capture(build_cmd(["--ssrManifest"]), str(out_dir))
        _summarize_build_lines(lines)
        if rc != 0:
            raise RuntimeError("Vite build failed.")
        rc, lines = _run_command_capture(
            build_cmd(["--ssr", ssr_entry, "--outDir", ssr_out_dir]), str(out_dir)
        )
        _summarize_build_lines(lines)
        if rc != 0:
            raise RuntimeError("Vite SSR build failed.")
        return

    rc, lines = _run_command_capture(build_cmd([]), str(out_dir))
    _summarize_build_lines(lines)
    if rc != 0:
        raise RuntimeError("Vite build failed.")


def _start_backend(
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


def install(args: Iterable[str]) -> None:
    """Install frontend dependencies using the detected package manager."""
    parsed = _parse_args(args)
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
    )
    if not (config.resolve_out_dir() / "package.json").exists():
        from nestipy.web.compiler import ensure_vite_files

        ensure_vite_files(config)
    _install_deps(config)


def add(args: Iterable[str]) -> None:
    """Add frontend dependencies to the Vite project."""
    parsed = _parse_args(args)
    packages = _collect_packages(args)
    if not packages:
        raise RuntimeError("Provide at least one package to add.")
    config = WebConfig(
        app_dir=str(parsed.get("app_dir", "app")),
        out_dir=str(parsed.get("out_dir", "web")),
        target=str(parsed.get("target", "vite")),
        clean=bool(parsed.get("clean", False)),
    )
    out_dir = config.resolve_out_dir()
    if not (out_dir / "package.json").exists():
        from nestipy.web.compiler import ensure_vite_files

        ensure_vite_files(config)
    if parsed.get("peer"):
        _add_peer_dependencies(out_dir, packages)
        _install_deps(config)
        return

    manager = _select_package_manager(out_dir)
    if manager == "pnpm":
        cmd = ["pnpm", "add"]
        if parsed.get("dev"):
            cmd.append("-D")
    elif manager == "yarn":
        cmd = ["yarn", "add"]
        if parsed.get("dev"):
            cmd.append("--dev")
    else:
        cmd = ["npm", "install"]
        if parsed.get("dev"):
            cmd.append("-D")
    cmd.extend(packages)
    subprocess.run(cmd, cwd=str(out_dir), check=False)


def _install_deps(config: WebConfig) -> None:
    """Install frontend dependencies with the selected package manager."""
    out_dir = config.resolve_out_dir()
    manager = _select_package_manager(out_dir)
    _web_log(f"Install: running {manager} install")
    if manager == "pnpm":
        cmd = ["pnpm", "install"]
    elif manager == "yarn":
        cmd = ["yarn", "install"]
    else:
        cmd = ["npm", "install"]
    rc, lines = _run_command_capture(cmd, str(out_dir))
    mode = _web_build_log_mode()
    if mode != "silent":
        added_line = next((l for l in lines if "added " in l and "package" in l), None)
        audited_line = next((l for l in lines if "audited " in l), None)
        vuln_line = next((l for l in lines if "vulnerabilities" in l), None)
        summary_parts = [p for p in (added_line, audited_line, vuln_line) if p]
        if summary_parts:
            _web_log(f"Install: {' | '.join(summary_parts)}")
        else:
            _web_log("Install: complete")
    if rc != 0:
        raise RuntimeError("Dependency install failed.")


def _select_package_manager(out_dir) -> str:
    """Choose a package manager based on existing lockfiles."""
    if (out_dir / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (out_dir / "yarn.lock").exists():
        return "yarn"
    return "npm"


def _add_peer_dependencies(out_dir, packages: list[str]) -> None:
    """Add peerDependencies entries to the package.json."""
    package_json = out_dir / "package.json"
    if not package_json.exists():
        raise RuntimeError("package.json not found in web output directory.")
    data = json.loads(package_json.read_text(encoding="utf-8"))
    peers = data.setdefault("peerDependencies", {})
    for spec in packages:
        name, version = _split_package_spec(spec)
        peers[name] = version
    package_json.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _split_package_spec(spec: str) -> tuple[str, str]:
    """Split a package spec into name and version (defaults to latest)."""
    if spec.startswith("@"):
        if "@" in spec[1:]:
            name, version = spec.rsplit("@", 1)
            return name, version or "latest"
        return spec, "latest"
    if "@" in spec:
        name, version = spec.split("@", 1)
        return name, version or "latest"
    return spec, "latest"
