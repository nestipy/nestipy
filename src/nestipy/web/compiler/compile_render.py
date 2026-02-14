"""JSX rendering helpers for the web compiler."""

from __future__ import annotations

import json
from typing import Any

from nestipy.web.ui import (
    COMPONENT_NAME_ATTR,
    ConditionalExpr,
    ExternalComponent,
    ForExpr,
    Fragment,
    JSExpr,
    LocalComponent,
    Node,
    Slot,
)
from .errors import CompilerError


def render_node(node: Node, slot_token: str | None = None) -> str:
    """Render a node tree into JSX."""
    if node.tag is Slot:
        return slot_token or ""

    if node.tag is Fragment:
        children = [render_child(child, slot_token=slot_token) for child in node.children]
        children = [c for c in children if c is not None]
        inner = "".join(children)
        return f"<>{inner}</>"

    tag = render_tag(node.tag)
    props = render_props(node.props)
    children = [render_child(child, slot_token=slot_token) for child in node.children]
    children = [c for c in children if c is not None]

    if not children:
        if props:
            return f"<{tag} {props} />"
        return f"<{tag} />"

    inner = "".join(children)
    if props:
        return f"<{tag} {props}>{inner}</{tag}>"
    return f"<{tag}>{inner}</{tag}>"


def render_root_value(value: Any, slot_token: str | None = None) -> str:
    """Render a root-level component return value."""
    if isinstance(value, Node):
        return render_node(value, slot_token=slot_token)
    if isinstance(value, ConditionalExpr):
        return render_conditional_expr(value)
    if isinstance(value, ForExpr):
        return render_for_expr(value)
    if isinstance(value, JSExpr):
        return str(value)
    return render_jsx_value(value)


def render_tag(tag: Any) -> str:
    """Render a tag or component reference for JSX."""
    if isinstance(tag, ExternalComponent):
        return tag.import_name
    if isinstance(tag, LocalComponent):
        return tag.name
    if isinstance(tag, JSExpr):
        return str(tag)
    if hasattr(tag, COMPONENT_NAME_ATTR):
        return getattr(tag, COMPONENT_NAME_ATTR)
    if isinstance(tag, str):
        return tag
    raise CompilerError(f"Unsupported tag type: {type(tag)}")


def render_props(props: dict[str, Any]) -> str:
    """Render JSX props from a props mapping."""
    rendered = []
    spreads = props.get("__spread__") if isinstance(props, dict) else None
    if spreads:
        for spread in spreads:
            rendered.append(f"{{...{spread}}}")
    for key, value in props.items():
        if key == "__spread__":
            continue
        result = render_prop(key, value)
        if result:
            rendered.append(result)
    return " ".join(rendered)


def render_prop(key: str, value: Any) -> str | None:
    """Render a single JSX prop key/value pair."""
    if value is None or value is False:
        return None
    if value is True:
        return key
    if isinstance(value, ConditionalExpr):
        return f"{key}={{{render_conditional_expr(value)}}}"
    if isinstance(value, ForExpr):
        return f"{key}={{{render_for_expr(value)}}}"
    if isinstance(value, JSExpr):
        return f"{key}={{{value}}}"
    if isinstance(value, str):
        return f"{key}={json.dumps(value)}"
    if isinstance(value, (int, float)):
        return f"{key}={{{value}}}"
    if isinstance(value, (dict, list)):
        return f"{key}={{{render_js_value(value)}}}"
    raise CompilerError(
        f"Unsupported prop type for '{key}': {type(value)}. Use js('...') for expressions."
    )


def render_js_value(value: Any) -> str:
    """Render a nested JS value for prop objects/arrays."""
    if isinstance(value, JSExpr):
        return str(value)
    if isinstance(value, ConditionalExpr):
        return render_conditional_expr(value)
    if isinstance(value, ForExpr):
        return render_for_expr(value)
    if isinstance(value, str):
        return json.dumps(value)
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(render_js_value(item) for item in value) + "]"
    if isinstance(value, dict):
        parts: list[str] = []
        spreads = value.get("__spread__") if isinstance(value, dict) else None
        if spreads:
            for spread in spreads:
                parts.append(f"...{spread}")
        for key, item in value.items():
            if key == "__spread__":
                continue
            parts.append(f"{json.dumps(key)}: {render_js_value(item)}")
        return "{" + ", ".join(parts) + "}"
    if isinstance(value, ExternalComponent):
        return value.import_name
    raise CompilerError(
        f"Unsupported value in JS object/array: {type(value)}. Use js('...') for expressions."
    )


def render_child(child: Any, slot_token: str | None = None) -> str | None:
    """Render a child node into JSX."""
    if child is None:
        return None
    if isinstance(child, Node):
        return render_node(child, slot_token=slot_token)
    if isinstance(child, JSExpr):
        return f"{{{child}}}"
    if isinstance(child, ConditionalExpr):
        return f"{{{render_conditional_expr(child)}}}"
    if isinstance(child, ForExpr):
        return f"{{{render_for_expr(child)}}}"
    if isinstance(child, str):
        return escape_text(child)
    if isinstance(child, (int, float)):
        return f"{{{child}}}"
    if isinstance(child, list):
        return "".join(filter(None, (render_child(c, slot_token=slot_token) for c in child)))
    return escape_text(str(child))


def escape_text(text: str) -> str:
    """Escape JSX text nodes."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_conditional_expr(expr: ConditionalExpr) -> str:
    """Render a conditional expression into a JS ternary."""
    return f"{expr.test} ? {render_jsx_value(expr.consequent)} : {render_jsx_value(expr.alternate)}"


def render_for_expr(expr: ForExpr) -> str:
    """Render a list comprehension into a JS map/filter chain."""
    iterable = str(expr.iterable)
    target = expr.target
    body = render_jsx_value(expr.body)
    if expr.condition is not None:
        condition = str(expr.condition)
        return f"{iterable}.filter(({target}) => {condition}).map(({target}) => {body})"
    return f"{iterable}.map(({target}) => {body})"


def render_jsx_value(value: Any) -> str:
    """Render a value for use inside JS expressions."""
    if isinstance(value, Node):
        return f"({render_node(value)})"
    if isinstance(value, ConditionalExpr):
        return f"({render_conditional_expr(value)})"
    if isinstance(value, ForExpr):
        return f"({render_for_expr(value)})"
    if isinstance(value, JSExpr):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value)
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(render_jsx_value(item) for item in value) + "]"
    if isinstance(value, dict):
        return render_js_value(value)
    raise CompilerError(
        f"Unsupported value in JSX expression: {type(value)}. Use js('...') for expressions."
    )


def indent(value: str, spaces: int) -> str:
    """Indent a multi-line string by a fixed number of spaces."""
    pad = " " * spaces
    return "\n".join(pad + line if line else line for line in value.split("\n"))
