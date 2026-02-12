"""Nestipy Web - Python-to-React frontend tooling (Vite target)."""

from .config import WebConfig
from .compiler import compile_app, build_routes, CompilerError
from .client import codegen_client, codegen_client_from_url
from .ui import component, h, external, js, props, Fragment, Slot

__all__ = [
    "WebConfig",
    "compile_app",
    "build_routes",
    "CompilerError",
    "codegen_client",
    "codegen_client_from_url",
    "component",
    "h",
    "external",
    "js",
    "props",
    "Fragment",
    "Slot",
]
