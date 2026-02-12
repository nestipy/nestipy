from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

COMPONENT_MARK_ATTR = "__nestipy_web_component__"
COMPONENT_NAME_ATTR = "__nestipy_web_component_name__"
PROPS_MARK_ATTR = "__nestipy_web_props__"


@dataclass(frozen=True, slots=True)
class ExternalComponent:
    module: str
    name: str
    default: bool = False
    alias: str | None = None

    @property
    def import_name(self) -> str:
        return self.alias or self.name

    def __call__(self, *children: Any, **props: Any) -> "Node":
        return Node(tag=self, props=_normalize_props(props), children=_flatten_children(children))


@dataclass(slots=True)
class Node:
    tag: Any
    props: dict[str, Any] = field(default_factory=dict)
    children: list[Any] = field(default_factory=list)


class JSExpr(str):
    """Raw JS expression marker for props."""


@dataclass(frozen=True, slots=True)
class LocalComponent:
    name: str

    def __call__(self, *children: Any, **props: Any) -> "Node":
        return Node(tag=self, props=_normalize_props(props), children=_flatten_children(children))


class _Fragment:
    pass


class _Slot:
    pass


Fragment = _Fragment()
Slot = _Slot()


def js(expr: str) -> JSExpr:
    return JSExpr(expr)


def external(module: str, name: str, *, default: bool = False, alias: str | None = None) -> ExternalComponent:
    return ExternalComponent(module=module, name=name, default=default, alias=alias)


def component(fn: Callable) -> Callable:
    setattr(fn, COMPONENT_MARK_ATTR, True)
    setattr(fn, COMPONENT_NAME_ATTR, fn.__name__)
    return fn


def props(cls: type) -> type:
    setattr(cls, PROPS_MARK_ATTR, True)
    return cls


def _flatten_children(children: Iterable[Any]) -> list[Any]:
    out: list[Any] = []
    for child in children:
        if child is None:
            continue
        if isinstance(child, (list, tuple)):
            out.extend(_flatten_children(child))
        else:
            out.append(child)
    return out


class H:
    def __call__(self, tag: Any, props: dict[str, Any] | None = None, *children: Any, **kwargs: Any) -> Node:
        actual_props: dict[str, Any] = {}
        if isinstance(props, dict):
            actual_props.update(props)
        elif props is not None:
            children = (props,) + children
        if kwargs:
            actual_props.update(_normalize_props(kwargs))
        return Node(tag=tag, props=actual_props, children=_flatten_children(children))

    def __getattr__(self, tag: str) -> Callable[..., Node]:
        def _tag(*children: Any, **kwargs: Any) -> Node:
            props: dict[str, Any] = {}
            if children and isinstance(children[0], dict):
                props.update(children[0])
                children = children[1:]
            if kwargs:
                props.update(_normalize_props(kwargs))
            return Node(tag=tag, props=props, children=_flatten_children(children))

        return _tag


def _normalize_props(props: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in props.items():
        normalized[_normalize_prop_key(key)] = value
    return normalized


def _normalize_prop_key(key: str) -> str:
    if key in {"class_name", "class_"}:
        return "className"
    if key == "for_":
        return "htmlFor"
    if key == "http_equiv":
        return "httpEquiv"
    if key == "accept_charset":
        return "acceptCharset"
    if key.startswith("data_"):
        return "data-" + key[5:].replace("_", "-")
    if key.startswith("aria_"):
        return "aria-" + key[5:].replace("_", "-")
    if key.endswith("_"):
        key = key[:-1]
    if "_" in key:
        parts = key.split("_")
        return parts[0] + "".join(part.capitalize() for part in parts[1:])
    return key


h = H()


__all__ = [
    "Node",
    "ExternalComponent",
    "JSExpr",
    "LocalComponent",
    "Fragment",
    "Slot",
    "COMPONENT_MARK_ATTR",
    "COMPONENT_NAME_ATTR",
    "PROPS_MARK_ATTR",
    "js",
    "external",
    "props",
    "component",
    "h",
]
