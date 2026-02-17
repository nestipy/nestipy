from __future__ import annotations

import asyncio
import inspect
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from nestipy.common.logger import logger


class SSRRenderError(RuntimeError):
    """Raised when SSR rendering fails."""


class SSRRenderer:
    """SSR renderer interface."""

    async def render(self, url: str) -> str | None:  # pragma: no cover - interface
        raise NotImplementedError


class JSRUNRenderer(SSRRenderer):
    """SSR renderer backed by jsrun (V8 via PyO3)."""

    def __init__(self, entry_path: str, module_name: str = "nestipy-ssr-entry") -> None:
        try:
            import jsrun  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise ImportError("jsrun is not installed. Install with nestipy[web-ssr].") from exc

        entry_file = Path(entry_path)
        if not entry_file.is_file():
            raise FileNotFoundError(f"SSR entry not found: {entry_path}")

        self._module_name = module_name
        self._exports: Optional[Dict[str, Any]] = None
        self._runtime = getattr(jsrun, "Runtime", None)
        if self._runtime is None:
            raise ImportError("jsrun.Runtime not found. Please update jsrun.")
        self._runtime = self._runtime()
        entry_code = entry_file.read_text(encoding="utf-8")
        if hasattr(self._runtime, "add_static_module"):
            polyfills = _load_jsrun_polyfills()
            code = polyfills + "\n" + entry_code
            self._runtime.add_static_module(self._module_name, code)
        else:
            raise ImportError("jsrun.Runtime.add_static_module not available.")

    async def _ensure_exports(self) -> Dict[str, Any]:
        if self._exports is not None:
            return self._exports
        runtime = self._runtime
        if hasattr(runtime, "eval_module_async"):
            exports = await runtime.eval_module_async(self._module_name)
        elif hasattr(runtime, "eval_module"):
            exports = runtime.eval_module(self._module_name)
        else:
            raise ImportError("jsrun.Runtime.eval_module_async not available.")
        if not isinstance(exports, dict):
            raise SSRRenderError("SSR module did not return exports.")
        self._exports = exports
        return exports

    async def render(self, url: str) -> str | None:
        exports = await self._ensure_exports()
        render_fn = exports.get("render")
        if render_fn is None:
            raise SSRRenderError("SSR entry does not export `render`.")
        result = render_fn(url)
        if inspect.isawaitable(result):
            result = await result
        if isinstance(result, dict):
            html = result.get("html") or result.get("body")
            return str(html) if html is not None else None
        return str(result) if result is not None else None


class NodeRenderer(SSRRenderer):
    """SSR renderer backed by a Node.js process."""

    def __init__(self, entry_path: str, node_binary: str | None = None) -> None:
        entry_file = Path(entry_path)
        if not entry_file.is_file():
            raise FileNotFoundError(f"SSR entry not found: {entry_path}")

        resolved_node = node_binary or os.getenv("NESTIPY_WEB_SSR_NODE") or shutil.which("node")
        if not resolved_node:
            raise ImportError("node is not installed or not found in PATH.")

        self._node = resolved_node
        self._entry_path = str(entry_file)
        timeout_raw = os.getenv("NESTIPY_WEB_SSR_TIMEOUT", "5") or "5"
        try:
            self._timeout = max(1.0, float(timeout_raw))
        except Exception:
            self._timeout = 5.0

        self._script = "\n".join(
            [
                "import { pathToFileURL } from 'url';",
                "const entry = process.argv[2];",
                "const url = process.argv[3] || '/';",
                "const entryUrl = pathToFileURL(entry).href;",
                "const mod = await import(entryUrl);",
                "if (!mod || typeof mod.render !== 'function') {",
                "  console.error('SSR entry does not export render()');",
                "  process.exit(1);",
                "}",
                "const result = await mod.render(url);",
                "let html = result;",
                "if (result && typeof result === 'object') {",
                "  html = result.html ?? result.body ?? '';",
                "}",
                "if (html === undefined || html === null) {",
                "  html = '';",
                "}",
                "process.stdout.write(String(html));",
            ]
        )

    async def render(self, url: str) -> str | None:
        return await asyncio.to_thread(self._render_sync, url)

    def _render_sync(self, url: str) -> str | None:
        try:
            result = subprocess.run(
                [self._node, "--input-type=module", "-e", self._script, self._entry_path, url],
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise SSRRenderError(f"SSR render timed out ({self._timeout}s).") from exc
        if result.returncode != 0:
            message = (result.stderr or "").strip() or "SSR render failed."
            raise SSRRenderError(message)
        return result.stdout


def create_ssr_renderer(runtime: str, entry_path: str) -> SSRRenderer:
    """Create an SSR renderer for the requested runtime."""
    runtime = (runtime or "jsrun").strip().lower()
    if runtime in {"auto"}:
        try:
            return JSRUNRenderer(entry_path)
        except ImportError:
            return NodeRenderer(entry_path)
    if runtime in {"jsrun", "v8"}:
        try:
            return JSRUNRenderer(entry_path)
        except ImportError:
            return NodeRenderer(entry_path)
    if runtime in {"node", "nodejs"}:
        return NodeRenderer(entry_path)
    raise ValueError(f"Unsupported SSR runtime: {runtime}")


def resolve_ssr_entry(dist_dir: str) -> str:
    """Resolve the default SSR entry from a dist directory."""
    return str(Path(dist_dir) / "ssr" / "entry-server.js")


def env_ssr_enabled() -> bool:
    """Check if SSR is enabled via environment."""
    return os.getenv("NESTIPY_WEB_SSR", "").strip().lower() in {"1", "true", "yes", "on"}


def env_ssr_runtime() -> str:
    return os.getenv("NESTIPY_WEB_SSR_RUNTIME", "jsrun").strip() or "jsrun"


def _default_polyfills_path() -> Path:
    return Path(__file__).parent / "runtime" / "polyfills.js"


def _load_jsrun_polyfills() -> str:
    """Load JS polyfills for the jsrun runtime."""
    env_path = os.getenv("NESTIPY_WEB_SSR_POLYFILLS", "").strip()
    if env_path:
        try:
            return Path(env_path).read_text(encoding="utf-8")
        except Exception as exc:
            logger.warning("[WEB] SSR polyfills not found (%s)", exc)
    try:
        return _default_polyfills_path().read_text(encoding="utf-8")
    except Exception as exc:
        logger.warning("[WEB] SSR polyfills missing (%s)", exc)
    return ""
