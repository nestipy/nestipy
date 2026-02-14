"""Shared dataclasses for the web compiler parser."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from nestipy.web.ui import ExternalComponent, ExternalFunction


@dataclass(slots=True)
class ImportSpec:
    """Describe a component import and its resolved file path."""

    name: str
    alias: str
    path: Path | None


@dataclass(slots=True)
class PropField:
    """Describe a typed prop field for a component props class."""

    name: str
    ts_type: str
    optional: bool


@dataclass(slots=True)
class PropsSpec:
    """Describe a component props interface."""

    name: str
    fields: list[PropField]


@dataclass(slots=True)
class ParsedModule:
    """Intermediate parse data for a module file."""

    externals: dict[str, ExternalComponent | ExternalFunction]
    functions: list[Any]
    imports: list[ImportSpec]
    props: dict[str, PropsSpec]


@dataclass(slots=True)
class ParsedFile:
    """Parsed component file with resolved nodes and metadata."""

    primary: str
    components: dict[str, Any]
    imports: list[ImportSpec]
    props: dict[str, PropsSpec]
    component_props: dict[str, str]
    hooks: dict[str, list[str]]
    module_prelude: list[str]
    externals: dict[str, ExternalComponent | ExternalFunction]
    component_prelude: dict[str, list[str]]
