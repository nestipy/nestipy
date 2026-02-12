from __future__ import annotations

import os
import time
import shlex
import subprocess
from typing import Iterable, Type

from nestipy.web.config import WebConfig
from nestipy.web.compiler import compile_app
from nestipy.web.client import codegen_client, codegen_client_from_url
from nestipy.web.actions_client import write_actions_client_file, codegen_actions_from_url


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
        elif arg == "--no-build":
            parsed["no_build"] = True
        elif arg == "--actions":
            parsed["actions"] = True
        elif arg == "--actions-output" and i + 1 < len(args_list):
            parsed["actions_output"] = args_list[i + 1]
            i += 1
        elif arg == "--actions-endpoint" and i + 1 < len(args_list):
            parsed["actions_endpoint"] = args_list[i + 1]
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
    compile_app(config)
    _maybe_codegen_client(parsed, config)
    _maybe_codegen_actions(parsed, config, modules)


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
        compile_app(config)


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

    def snapshot() -> dict[str, float]:
        """Capture modification times for app source files."""
        state: dict[str, float] = {}
        for path in app_dir.rglob("*.py"):
            try:
                state[str(path)] = path.stat().st_mtime
            except FileNotFoundError:
                continue
        return state

    last_state = snapshot()
    compile_app(config)
    _maybe_codegen_client(parsed, config)
    _maybe_codegen_actions(parsed, config, modules)
    if parsed.get("vite"):
        if parsed.get("install"):
            _install_deps(config)
        vite_process = _start_vite(config)
    if backend_cmd:
        backend_process = _start_backend(
            str(backend_cmd),
            cwd=str(backend_cwd) if backend_cwd else None,
        )
    try:
        while True:
            time.sleep(0.5)
            current = snapshot()
            if current != last_state:
                compile_app(config)
                _maybe_codegen_client(parsed, config)
                _maybe_codegen_actions(parsed, config, modules)
                last_state = current
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
        raise RuntimeError("Modules are required to generate actions client")
    endpoint = str(parsed.get("actions_endpoint", "/_actions"))
    write_actions_client_file(modules, str(output), endpoint=endpoint)


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


def _start_backend(command: str, cwd: str | None = None) -> subprocess.Popen[str]:
    """Start the backend process from a shell command."""
    cmd = shlex.split(command)
    return subprocess.Popen(cmd, cwd=cwd)


def _install_deps(config: WebConfig) -> None:
    """Install frontend dependencies with the selected package manager."""
    out_dir = config.resolve_out_dir()
    manager = _select_package_manager(out_dir)
    if manager == "pnpm":
        cmd = ["pnpm", "install"]
    elif manager == "yarn":
        cmd = ["yarn", "install"]
    else:
        cmd = ["npm", "install"]
    subprocess.run(cmd, cwd=str(out_dir), check=False)


def _select_package_manager(out_dir) -> str:
    """Choose a package manager based on existing lockfiles."""
    if (out_dir / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (out_dir / "yarn.lock").exists():
        return "yarn"
    return "npm"
