from __future__ import annotations

import os
import traceback
from typing import Iterable, Type

from nestipy.common.logger import logger
from nestipy.web.compiler import CompilerError, compile_app
from nestipy.web.config import WebConfig

from .command_args import parse_args
from .command_codegen import maybe_codegen_actions, maybe_codegen_client
from .command_pkg import install_deps
from .command_shell import (
    log_build_failure,
    run_command_capture,
    select_package_manager,
    summarize_build_lines,
)
from .command_templates import DEFAULT_ACTIONS_TEMPLATE, DEFAULT_LAYOUT_TEMPLATE, DEFAULT_PAGE_TEMPLATE


def build(args: Iterable[str], modules: list[Type] | None = None) -> None:
    """Build the frontend and optionally generate clients."""
    parsed = parse_args(args)
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
    if modules is not None:
        actions_output = parsed.get("actions_output")
        if not actions_output:
            actions_output = str(config.resolve_src_dir() / "actions.client.ts")
        actions_types_output = parsed.get("actions_types")
        if not actions_types_output:
            actions_types_output = str(config.resolve_app_dir() / "_generated" / "actions_types.py")
        actions_endpoint = str(parsed.get("actions_endpoint", "/_actions"))
        from nestipy.web.actions_client import write_actions_client_file

        write_actions_client_file(modules, str(actions_output), endpoint=actions_endpoint)
        from nestipy.web.actions_client import write_actions_types_file

        write_actions_types_file(modules, str(actions_types_output), endpoint=actions_endpoint)

        client_output = parsed.get("output")
        if not client_output:
            client_output = str(config.resolve_src_dir() / "api" / "client.ts")
        client_types_output = parsed.get("router_types")
        if not client_types_output:
            client_types_output = str(config.resolve_app_dir() / "_generated" / "api_types.py")
        client_language = str(parsed.get("lang", "ts"))
        class_name = str(parsed.get("class_name", "ApiClient"))
        prefix = str(parsed.get("prefix", ""))
        from nestipy.web.client import codegen_client

        codegen_client(
            modules,
            str(client_output),
            language=client_language,
            class_name=class_name,
            prefix=prefix,
        )
        from nestipy.web.client_types import write_client_types_file

        write_client_types_file(
            modules,
            str(client_types_output),
            class_name=class_name,
            prefix=prefix,
        )
    else:
        maybe_codegen_client(parsed, config)
        maybe_codegen_actions(parsed, config, modules)
    vite_enabled = bool(parsed.get("vite") or config.target == "vite")
    if vite_enabled:
        from nestipy.web.compiler import ensure_vite_files

        ensure_vite_files(config)
        if parsed.get("install"):
            install_deps(config)
        ssr_enabled = bool(parsed.get("ssr"))
        ssr_entry = str(parsed.get("ssr_entry") or "src/entry-server.tsx")
        ssr_out_dir = str(parsed.get("ssr_out_dir") or "dist/ssr")
        build_vite(config, ssr=ssr_enabled, ssr_entry=ssr_entry, ssr_out_dir=ssr_out_dir)
        validate_vite_output(config, ssr=ssr_enabled, ssr_out_dir=ssr_out_dir)
        maybe_set_web_dist(config)


def init(args: Iterable[str]) -> None:
    """Scaffold a minimal Nestipy Web app."""
    parsed = parse_args(args)
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
    app_init = app_dir / "__init__.py"
    if not app_init.exists():
        app_init.write_text("", encoding="utf-8")

    page_file = app_dir / "page.py"
    if not page_file.exists():
        page_file.write_text(DEFAULT_PAGE_TEMPLATE, encoding="utf-8")

    layout_file = app_dir / "layout.py"
    if not layout_file.exists():
        layout_file.write_text(DEFAULT_LAYOUT_TEMPLATE, encoding="utf-8")

    actions_file = app_dir / "actions.py"
    if not actions_file.exists():
        actions_file.write_text(DEFAULT_ACTIONS_TEMPLATE, encoding="utf-8")
    generated_dir = app_dir / "_generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    init_file = generated_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("", encoding="utf-8")
    actions_types_file = generated_dir / "actions_types.py"
    if not actions_types_file.exists():
        actions_types_file.write_text(
            "\n".join(
                [
                    "from __future__ import annotations",
                    "",
                    "from typing import Any, Protocol, TypeVar, Generic, Callable",
                    "",
                    "T = TypeVar(\"T\")",
                    "",
                    "class ActionError(Protocol):",
                    "    message: str",
                    "    type: str",
                    "",
                    "class ActionResponse(Protocol, Generic[T]):",
                    "    ok: bool",
                    "    data: T | None",
                    "    error: ActionError | None",
                    "",
                    "class JsPromise(Protocol, Generic[T]):",
                    "    def then(",
                    "        self,",
                    "        on_fulfilled: Callable[[T], Any] | None = ...,",
                    "        on_rejected: Callable[[Any], Any] | None = ...,",
                    "    ) -> \"JsPromise[Any]\": ...",
                    "",
                    "class ActionsClient(Protocol):",
                    "    pass",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    api_types_file = generated_dir / "api_types.py"
    if not api_types_file.exists():
        api_types_file.write_text(
            "\n".join(
                [
                    "from __future__ import annotations",
                    "",
                    "from typing import Any, Protocol, TypeVar, Generic, Callable",
                    "",
                    "T = TypeVar(\"T\")",
                    "",
                    "class JsPromise(Protocol, Generic[T]):",
                    "    def then(",
                    "        self,",
                    "        on_fulfilled: Callable[[T], Any] | None = ...,",
                    "        on_rejected: Callable[[Any], Any] | None = ...,",
                    "    ) -> \"JsPromise[Any]\": ...",
                    "",
                    "class ApiClient(Protocol):",
                    "    pass",
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


def build_vite(
    config: WebConfig,
    *,
    ssr: bool = False,
    ssr_entry: str = "src/entry-server.tsx",
    ssr_out_dir: str = "dist/ssr",
) -> None:
    """Run the Vite production build using the detected package manager."""
    out_dir = config.resolve_out_dir()
    manager = select_package_manager(out_dir)

    def build_cmd(extra: list[str]) -> list[str]:
        args = ["--", *extra] if extra else []
        if manager == "pnpm":
            return ["pnpm", "build", *args]
        if manager == "yarn":
            return ["yarn", "build", *args]
        return ["npm", "run", "build", *args]

    if ssr:
        rc, lines = run_command_capture(build_cmd(["--ssrManifest"]), str(out_dir))
        summarize_build_lines(lines)
        if rc != 0:
            log_build_failure(lines)
            raise RuntimeError("Vite build failed.")
        rc, lines = run_command_capture(
            build_cmd(["--ssr", ssr_entry, "--outDir", ssr_out_dir]), str(out_dir)
        )
        summarize_build_lines(lines)
        if rc != 0:
            log_build_failure(lines)
            raise RuntimeError("Vite SSR build failed.")
        return

    rc, lines = run_command_capture(build_cmd([]), str(out_dir))
    summarize_build_lines(lines)
    if rc != 0:
        log_build_failure(lines)
        raise RuntimeError("Vite build failed.")


def maybe_set_web_dist(config: WebConfig) -> None:
    """Set NESTIPY_WEB_DIST to the build output directory if not already set."""
    if os.getenv("NESTIPY_WEB_DIST"):
        return
    dist_path = config.resolve_out_dir() / "dist"
    if dist_path.exists():
        os.environ["NESTIPY_WEB_DIST"] = str(dist_path)


def validate_vite_output(
    config: WebConfig,
    *,
    ssr: bool = False,
    ssr_out_dir: str = "dist/ssr",
) -> None:
    """Ensure Vite output exists and basic manifests are present."""
    out_dir = config.resolve_out_dir()
    dist_dir = out_dir / "dist"
    if not dist_dir.exists():
        raise RuntimeError("Vite build did not produce a dist directory.")
    index_file = dist_dir / "index.html"
    if not index_file.exists():
        raise RuntimeError("Vite build missing dist/index.html.")
    manifest_candidates = [
        dist_dir / "manifest.json",
        dist_dir / ".vite" / "manifest.json",
    ]
    if not any(path.exists() for path in manifest_candidates):
        raise RuntimeError("Vite build missing manifest.json.")
    if ssr:
        ssr_dir = out_dir / ssr_out_dir
        if not ssr_dir.exists():
            raise RuntimeError("Vite SSR build missing ssr output directory.")
