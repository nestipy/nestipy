from __future__ import annotations

from pathlib import Path
import json

from nestipy.web.config import WebConfig
from .compile_assets import ensure_vite_files
from .compile_components import (
    build_page_tsx,
    collect_used_components,
    compile_component_module,
    component_import_path,
    merge_component_imports,
    render_page_tree,
    resolve_component_imports,
)
from .compile_routes import build_routes, discover_routes, _compile_layouts, _compile_notfound
from .compile_types import ErrorInfo, RouteInfo
from .errors import CompilerError
from .parser import ParsedFile


def compile_app(config: WebConfig, root: str | None = None) -> list[RouteInfo]:
    """Compile the web app sources into a Vite-ready project."""
    app_dir = config.resolve_app_dir(root)
    out_dir = config.resolve_out_dir(root)
    pages_dir = config.resolve_pages_dir(root)

    if not app_dir.exists():
        raise CompilerError(f"App directory not found: {app_dir}")

    if config.clean and out_dir.exists():
        for item in out_dir.rglob("*"):
            if item.is_file():
                item.unlink()

    out_dir.mkdir(parents=True, exist_ok=True)
    pages_dir.mkdir(parents=True, exist_ok=True)

    routes = discover_routes(app_dir, pages_dir)
    src_dir = config.resolve_src_dir(root)
    component_cache: dict[Path, tuple[ParsedFile, Path]] = {}
    visiting: set[Path] = set()
    layout_infos = _compile_layouts(
        app_dir=app_dir,
        src_dir=src_dir,
        cache=component_cache,
        visiting=visiting,
        routes_file=config.resolve_src_dir(root) / "routes.tsx",
    )
    notfound_infos = _compile_notfound(
        app_dir=app_dir,
        src_dir=src_dir,
        cache=component_cache,
        visiting=visiting,
        routes_file=config.resolve_src_dir(root) / "routes.tsx",
    )

    for info in routes:
        parsed_page = render_page_tree(info.source, app_dir)
        page_imports, page_imported_props = resolve_component_imports(
            parsed_page,
            used_names=collect_used_components(parsed_page.components.values()),
            local_names=set(parsed_page.components.keys()),
            app_dir=app_dir,
            src_dir=src_dir,
            from_output=info.output,
            cache=component_cache,
            visiting=visiting,
        )
        component_imports = merge_component_imports(page_imports)
        imported_props = dict(page_imported_props)
        tsx = build_page_tsx(
            parsed_page,
            root_layout=None,
            component_imports=component_imports,
            imported_props=imported_props,
        )
        info.output.parent.mkdir(parents=True, exist_ok=True)
        info.output.write_text(tsx, encoding="utf-8")

    error_info: ErrorInfo | None = None
    error_file = app_dir / "error.py"
    if error_file.exists():
        parsed, out_path = compile_component_module(
            error_file,
            app_dir=app_dir,
            src_dir=src_dir,
            cache=component_cache,
            visiting=visiting,
            target_names=("ErrorBoundary", "Error", "error"),
        )
        import_path = component_import_path(
            config.resolve_src_dir(root) / "routes.tsx", out_path
        )
        error_info = ErrorInfo(
            export_name=parsed.primary,
            import_alias="AppErrorBoundary",
            import_path=import_path,
        )

    build_routes(
        routes,
        config,
        root,
        layout_infos=layout_infos,
        error_info=error_info,
        notfound_infos=notfound_infos,
    )
    _write_ssr_routes(routes, config, root)
    ensure_vite_files(config, root)
    return routes


def _write_ssr_routes(routes: list[RouteInfo], config: WebConfig, root: str | None) -> None:
    """Persist SSR opt-in routes to web/public for runtime lookup."""
    entries = [
        {"path": info.route, "ssr": info.ssr}
        for info in routes
        if info.ssr is not None
    ]
    if not entries:
        return
    out_dir = config.resolve_out_dir(root)
    public_dir = out_dir / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    payload = {"routes": entries}
    (public_dir / "ssr-routes.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
