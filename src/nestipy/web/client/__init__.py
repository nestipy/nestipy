from __future__ import annotations

from typing import Type
import json
import urllib.request
import os

from nestipy.router import build_router_spec, write_client_file, write_typescript_client_file


def codegen_client(
    modules: list[Type],
    output: str,
    *,
    language: str = "python",
    class_name: str = "ApiClient",
    prefix: str = "",
) -> None:
    """Generate a typed API client file from router metadata."""
    spec = build_router_spec(modules, prefix=prefix)
    _ensure_parent(output)
    if language in {"ts", "typescript"}:
        write_typescript_client_file(spec, output, class_name=class_name)
    else:
        write_client_file(spec, output, class_name=class_name, async_client=False)


def codegen_client_from_url(
    url: str, output: str, *, language: str = "python", class_name: str = "ApiClient"
) -> None:
    """Generate a typed API client file from a router spec URL."""
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode("utf-8"))
    _ensure_parent(output)
    if language in {"ts", "typescript"}:
        write_typescript_client_file(data, output, class_name=class_name)
    else:
        write_client_file(data, output, class_name=class_name, async_client=False)


def _ensure_parent(output: str) -> None:
    """Ensure the destination directory exists before writing output."""
    path = os.path.abspath(output)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


__all__ = ["codegen_client", "codegen_client_from_url"]
