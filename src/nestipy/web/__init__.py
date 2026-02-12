"""Nestipy Web - Python-to-React frontend tooling (Vite target)."""

from .config import WebConfig
from .compiler import compile_app, build_routes, CompilerError
from .ui import component, h, external, js, props, Fragment, Slot

__all__ = [
    "WebConfig",
    "compile_app",
    "build_routes",
    "CompilerError",
    "component",
    "h",
    "external",
    "js",
    "props",
    "Fragment",
    "Slot",
]


def codegen_client(*args, **kwargs):
    from .client import codegen_client as _codegen_client

    return _codegen_client(*args, **kwargs)


def codegen_client_from_url(*args, **kwargs):
    from .client import codegen_client_from_url as _codegen_client_from_url

    return _codegen_client_from_url(*args, **kwargs)


__all__.extend(["codegen_client", "codegen_client_from_url"])
