from __future__ import annotations

import inspect
import os
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
            shim_code = "\n".join(
                [
                    "if (typeof globalThis.process === 'undefined') {",
                    "  globalThis.process = { env: { NODE_ENV: 'production' } };",
                    "} else {",
                    "  globalThis.process.env = globalThis.process.env || {};",
                    "  if (!('NODE_ENV' in globalThis.process.env)) {",
                    "    globalThis.process.env.NODE_ENV = 'production';",
                    "  }",
                    "}",
                    "if (typeof globalThis.global === 'undefined') {",
                    "  globalThis.global = globalThis;",
                    "}",
                    "if (typeof globalThis.queueMicrotask === 'undefined') {",
                    "  globalThis.queueMicrotask = (cb) => Promise.resolve().then(cb);",
                    "}",
                    "if (typeof globalThis.MessageChannel === 'undefined') {",
                    "  class MessagePort {",
                    "    constructor() { this.onmessage = null; this._other = null; }",
                    "    postMessage(data) {",
                    "      const handler = this._other && this._other.onmessage;",
                    "      if (!handler) return;",
                    "      const event = { data };",
                    "      if (typeof globalThis.queueMicrotask === 'function') {",
                    "        globalThis.queueMicrotask(() => handler(event));",
                    "      } else if (typeof setTimeout === 'function') {",
                    "        setTimeout(() => handler(event), 0);",
                    "      } else {",
                    "        handler(event);",
                    "      }",
                    "    }",
                    "    start() {}",
                    "    close() {}",
                    "  }",
                    "  class MessageChannel {",
                    "    constructor() {",
                    "      this.port1 = new MessagePort();",
                    "      this.port2 = new MessagePort();",
                    "      this.port1._other = this.port2;",
                    "      this.port2._other = this.port1;",
                    "    }",
                    "  }",
                    "  globalThis.MessageChannel = MessageChannel;",
                    "}",
                ]
            )
            code = shim_code + "\n" + entry_code
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


def create_ssr_renderer(runtime: str, entry_path: str) -> SSRRenderer:
    """Create an SSR renderer for the requested runtime."""
    runtime = (runtime or "jsrun").strip().lower()
    if runtime in {"jsrun", "v8"}:
        return JSRUNRenderer(entry_path)
    raise ValueError(f"Unsupported SSR runtime: {runtime}")


def resolve_ssr_entry(dist_dir: str) -> str:
    """Resolve the default SSR entry from a dist directory."""
    return str(Path(dist_dir) / "ssr" / "entry-server.js")


def env_ssr_enabled() -> bool:
    """Check if SSR is enabled via environment."""
    return os.getenv("NESTIPY_WEB_SSR", "").strip().lower() in {"1", "true", "yes", "on"}


def env_ssr_runtime() -> str:
    return os.getenv("NESTIPY_WEB_SSR_RUNTIME", "jsrun").strip() or "jsrun"
