"""Shared dataclasses for the web compiler."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class RouteInfo:
    """Represent a resolved route and its compiled output path."""

    route: str
    source: Path
    output: Path
    import_path: str
    component_name: str
    ssr: bool | None = None


@dataclass(slots=True)
class ComponentImport:
    """Describe a component import used in generated TSX."""

    import_path: str
    names: list[tuple[str, str]]


@dataclass(slots=True)
class LayoutInfo:
    """Describe a compiled layout component."""

    raw_parts: tuple[str, ...]
    export_name: str
    import_alias: str
    import_path: str


@dataclass(slots=True)
class ErrorInfo:
    """Describe a compiled error boundary component."""

    export_name: str
    import_alias: str
    import_path: str


@dataclass(slots=True)
class NotFoundInfo:
    """Describe a compiled notfound component."""

    raw_parts: tuple[str, ...]
    export_name: str
    import_alias: str
    import_path: str


@dataclass(slots=True)
class LayoutNode:
    """Tree node for nested layouts."""

    raw_parts: tuple[str, ...]
    info: LayoutInfo | None
    children: list["LayoutNode"]
    pages: list[tuple[str | None, str]]
