from __future__ import annotations

import os
import mimetypes
from typing import Callable, Optional, Type

import aiofiles

from nestipy.common.constant import DEVTOOLS_STATIC_PATH_KEY
from nestipy.common.logger import logger
from nestipy.common.http_ import Request, Response
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ModuleMetadata, Reflect
from nestipy.router.spec import RouterSpec
from nestipy.core.adapter.http_adapter import HttpAdapter
from nestipy.core.types import JsonValue, ModuleRef, ProviderToken, TokenProvider


def resolve_devtools_static_path(config_path: Optional[str]) -> str:
    if config_path:
        return "/" + config_path.strip("/")
    env_path = os.getenv("NESTIPY_DEVTOOLS_STATIC_PATH")
    if env_path:
        return env_path if env_path.startswith("/") else f"/{env_path.strip('/')}"
    env_token = os.getenv("NESTIPY_DEVTOOLS_TOKEN")
    token = env_token or read_or_create_devtools_token()
    return f"/_devtools/{token}/static"


def read_or_create_devtools_token() -> str:
    import hashlib

    cwd = os.path.abspath(os.getcwd())
    digest = hashlib.sha256(cwd.encode("utf-8")).hexdigest()
    # Stable, deterministic token across workers to avoid asset 404s.
    return digest[:32]


class DevtoolsRegistrar:
    """Register devtools routes (static assets, graph UI, router spec)."""
    def __init__(
        self,
        *,
        http_adapter: HttpAdapter,
        devtools_static_path: str,
        devtools_graph_renderer: str,
        router_spec_enabled: bool,
        router_spec_path: str,
        router_spec_token: Optional[str],
        get_router_spec: Callable[[], RouterSpec],
        get_root_module: Callable[[], Optional[Type]],
    ) -> None:
        self._http_adapter = http_adapter
        self._devtools_static_path = devtools_static_path
        self._devtools_graph_renderer = devtools_graph_renderer
        self._router_spec_enabled = router_spec_enabled
        self._router_spec_path = router_spec_path
        self._router_spec_token = router_spec_token
        self._get_router_spec = get_router_spec
        self._get_root_module = get_root_module

    def register_static(self) -> None:
        """Serve devtools static assets."""
        static_dir = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "devtools",
                "frontend",
                "static",
            )
        )
        static_path = self._devtools_static_path
        self._http_adapter.set(DEVTOOLS_STATIC_PATH_KEY, static_path)

        async def devtools_static_handler(req: Request, res: Response, _next_fn):
            rel_path = req.path_params.get("path", "").lstrip("/")
            if not rel_path and req.path.startswith(static_path):
                rel_path = req.path[len(static_path) :].lstrip("/")
            if not rel_path:
                return await res.status(404).send("Not found")
            file_path = os.path.realpath(os.path.join(static_dir, rel_path))
            if not file_path.startswith(static_dir) or not os.path.isfile(file_path):
                return await res.status(404).send("Not found")
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            ext = os.path.splitext(file_path)[1].lower()
            if ext in {".js", ".css", ".html"}:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                content = content.replace("/_devtools/static", static_path)
                return await res.header("Content-Type", mime_type).send(content)
            async with aiofiles.open(file_path, "rb") as f:
                payload = await f.read()
            res.header("Content-Type", mime_type)
            await res._write(payload)
            return res

        static_route = self._http_adapter.create_wichard(
            static_path.strip("/"), name="path"
        )
        if not static_route.startswith("/"):
            static_route = "/" + static_route
        raw_meta = {"raw": True}
        self._http_adapter.get(static_route, devtools_static_handler, raw_meta)
        self._http_adapter.head(static_route, devtools_static_handler, raw_meta)

        async def devtools_static_fallback(req: Request, res: Response, _next_fn):
            path = req.path or ""
            marker = "/static/"
            idx = path.find(marker)
            if idx < 0:
                return await res.status(404).send("Not found")
            rel_path = path[idx + len(marker) :].lstrip("/")
            if not rel_path:
                return await res.status(404).send("Not found")
            file_path = os.path.realpath(os.path.join(static_dir, rel_path))
            if not file_path.startswith(static_dir) or not os.path.isfile(file_path):
                return await res.status(404).send("Not found")
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "application/octet-stream"
            ext = os.path.splitext(file_path)[1].lower()
            if ext in {".js", ".css", ".html"}:
                async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                    content = await f.read()
                # Normalize to current static path for relative links
                content = content.replace("/_devtools/static", static_path)
                return await res.header("Content-Type", mime_type).send(content)
            async with aiofiles.open(file_path, "rb") as f:
                payload = await f.read()
            res.header("Content-Type", mime_type)
            await res._write(payload)
            return res

        fallback_route = self._http_adapter.create_wichard("_devtools", name="path")
        if not fallback_route.startswith("/"):
            fallback_route = "/" + fallback_route
        self._http_adapter.get(fallback_route, devtools_static_fallback, raw_meta)
        self._http_adapter.head(fallback_route, devtools_static_fallback, raw_meta)

    def register_graph(self) -> None:
        """Serve devtools dependency graph (HTML + JSON)."""
        root_path = self._devtools_static_path
        if root_path.endswith("/static"):
            root_path = root_path[: -len("/static")]
        if not root_path:
            root_path = "/_devtools"
        graph_path = f"{root_path.rstrip('/')}/graph"
        graph_json_path = f"{root_path.rstrip('/')}/graph.json"

        async def graph_json_handler(_req: Request, res: Response, _next_fn):
            dependency_graph = NestipyContainer.get_instance().get_dependency_graph()
            module_graph = self._build_module_graph()
            return await res.json(
                {
                    "graph": dependency_graph,
                    "dependency_graph": dependency_graph,
                    "modules": module_graph,
                }
            )

        async def graph_html_handler(req: Request, res: Response, _next_fn):
            static_root = self._devtools_static_path
            renderer = (req.query_params.get("renderer") or self._devtools_graph_renderer).lower()
            if renderer not in {"mermaid", "cytoscape"}:
                renderer = self._devtools_graph_renderer
            template_dir = os.path.realpath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "devtools",
                    "frontend",
                    "templates",
                )
            )
            template_name = "graph-cytoscape.html"
            if renderer == "mermaid":
                template_name = "graph-mermaid.html"
            template_path = os.path.join(template_dir, template_name)
            with open(template_path, "r", encoding="utf-8") as handle:
                html = handle.read()
            html = (
                html.replace("__NESTIPY_STATIC_ROOT__", static_root)
                .replace("__NESTIPY_GRAPH_JSON__", graph_json_path)
                .replace("__NESTIPY_GRAPH_PATH__", graph_path)
            )
            return await res.header("Content-Type", "text/html; charset=utf-8").send(html)

        raw_meta = {"raw": True}
        self._http_adapter.get(graph_path, graph_html_handler, raw_meta)
        self._http_adapter.get(graph_json_path, graph_json_handler, raw_meta)

    def register_router_spec(self) -> None:
        """Serve router spec JSON when enabled."""
        if not self._router_spec_enabled:
            return

        path = self._router_spec_path

        async def router_spec_handler(req: Request, res: Response, _next_fn):
            if self._router_spec_token:
                headers = {k.lower(): v for k, v in req.headers.items()}
                header_token = headers.get("x-router-spec-token")
                query_token = req.query_params.get("token")
                if self._router_spec_token not in {header_token, query_token}:
                    return await res.status(403).send("Forbidden")
            from nestipy.router import router_spec_to_dict

            spec = self._get_router_spec()
            return await res.json(router_spec_to_dict(spec))

        self._http_adapter.get(path, router_spec_handler, {"raw": True})

    def _build_module_graph(self) -> dict[str, JsonValue]:
        root_module = self._get_root_module()
        if root_module is None:
            return {"root": None, "nodes": [], "edges": []}

        def module_name(mod: ModuleRef) -> str:
            return getattr(mod, "__name__", str(mod))

        def module_id(mod: ModuleRef) -> str:
            return f"module:{module_name(mod)}"

        def token_name(token: ProviderToken | None) -> str:
            if token is None:
                return "Unknown"
            if hasattr(token, "__name__"):
                return token.__name__
            return str(token)

        def provider_name(provider: ProviderToken | TokenProvider) -> str:
            if hasattr(provider, "token"):
                return token_name(provider.token)
            return token_name(provider)

        nodes: list[dict[str, JsonValue]] = []
        edges: list[dict[str, JsonValue]] = []
        module_seen: set[type] = set()
        node_ids: set[str] = set()

        def add_node(node: dict[str, JsonValue]) -> None:
            node_id = node["id"]
            if node_id in node_ids:
                return
            node_ids.add(node_id)
            nodes.append(node)

        def visit(module_ref: ModuleRef) -> None:
            module = module_ref.module if hasattr(module_ref, "module") else module_ref
            if module is None:
                return
            if module not in module_seen:
                module_seen.add(module)
                add_node(
                    {
                        "id": module_id(module),
                        "label": module_name(module),
                        "type": "module",
                        "global": Reflect.get_metadata(module, ModuleMetadata.Global, False),
                    }
                )

            module_key = module_name(module)
            for controller in Reflect.get_metadata(module, ModuleMetadata.Controllers, []):
                ctrl_label = token_name(controller)
                ctrl_id = f"controller:{module_key}:{ctrl_label}"
                add_node(
                    {
                        "id": ctrl_id,
                        "label": ctrl_label,
                        "type": "controller",
                        "module": module_key,
                    }
                )
                edges.append(
                    {
                        "source": module_id(module),
                        "target": ctrl_id,
                        "type": "controller",
                    }
                )

            for provider in Reflect.get_metadata(module, ModuleMetadata.Providers, []):
                prov_label = provider_name(provider)
                prov_id = f"provider:{module_key}:{prov_label}"
                add_node(
                    {
                        "id": prov_id,
                        "label": prov_label,
                        "type": "provider",
                        "module": module_key,
                    }
                )
                edges.append(
                    {
                        "source": module_id(module),
                        "target": prov_id,
                        "type": "provider",
                    }
                )

            for imp in Reflect.get_metadata(module, ModuleMetadata.Imports, []):
                imp_module = imp.module if hasattr(imp, "module") else imp
                if imp_module is None:
                    continue
                edges.append(
                    {
                        "source": module_id(module),
                        "target": module_id(imp_module),
                        "type": "import",
                    }
                )
                visit(imp_module)

        visit(root_module)
        return {"root": module_id(root_module), "nodes": nodes, "edges": edges}


__all__ = ["DevtoolsRegistrar", "resolve_devtools_static_path", "read_or_create_devtools_token"]
