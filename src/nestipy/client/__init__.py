"""Typed TypeScript client generation for Nestipy.

Generates a typed TypeScript HTTP client from your controller route metadata
(``@Controller`` / ``@Get`` / ``@Post`` ...), so a JS/TS frontend can call the
API with full typing. This is a thin, public facade over :mod:`nestipy.router`.
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Type, Union

from nestipy.router import (
    build_router_spec,
    generate_typescript_client_code,
    router_spec_from_dict,
    write_typescript_client_file,
)

__all__ = [
    "generate_client",
    "generate_client_from_url",
    "generate_typescript_client_code",
]


def _ensure_parent(output: str) -> None:
    parent = os.path.dirname(os.path.abspath(output))
    if parent:
        os.makedirs(parent, exist_ok=True)


def _normalize(modules: list[Union[Type, object]]) -> list:
    return [m() if isinstance(m, type) else m for m in modules]


def generate_client(
    modules: list[Union[Type, object]],
    output: str,
    *,
    class_name: str = "ApiClient",
    prefix: str = "",
) -> None:
    """Generate a typed TypeScript HTTP client from controller route metadata.

    :param modules: Root module(s) (classes or instances) to introspect.
    :param output: Path to the ``.ts`` file to write.
    :param class_name: Name of the generated client class.
    :param prefix: Optional route prefix to prepend to every path.
    """
    spec = build_router_spec(_normalize(modules), prefix=prefix)
    _ensure_parent(output)
    write_typescript_client_file(spec, output, class_name=class_name)


def generate_client_from_url(
    url: str,
    output: str,
    *,
    class_name: str = "ApiClient",
) -> None:
    """Generate a typed TypeScript client from a running server's router spec.

    :param url: URL of a router-spec endpoint returning JSON (see
        ``NestipyConfig(router_spec_enabled=True)``).
    :param output: Path to the ``.ts`` file to write.
    :param class_name: Name of the generated client class.
    """
    with urllib.request.urlopen(url) as response:  # noqa: S310 - user-provided URL
        data = json.loads(response.read().decode("utf-8"))
    spec = router_spec_from_dict(data)
    _ensure_parent(output)
    write_typescript_client_file(spec, output, class_name=class_name)
