from __future__ import annotations

from pathlib import Path

from nestipy.web import WebConfig
from nestipy.web.compiler import compile_app


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_compile_basic_app(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    return h.div("Hello", class_name="p-4")
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    routes = compile_app(config, root=str(tmp_path))

    assert routes
    assert (out_dir / "index.html").exists()
    assert (out_dir / "src" / "main.tsx").exists()
    assert (out_dir / "src" / "routes.tsx").exists()
    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "export default function Page" in page_tsx
    assert "<div" in page_tsx


def test_compile_with_layout(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "layout.py",
        """
from nestipy.web import component, h, Slot

@component
def Layout():
    return h.div(
        h.main(h(Slot)),
        class_name="layout",
    )
""".strip(),
    )

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    return h.section("Content")
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    routes_tsx = (out_dir / "src" / "routes.tsx").read_text(encoding="utf-8")
    assert "Layout" in routes_tsx
    assert "children" in routes_tsx

    layout_tsx = (out_dir / "src" / "components" / "layout.tsx").read_text(
        encoding="utf-8"
    )
    assert "Outlet" in layout_tsx


def test_compile_with_nested_component(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Header():
    return h.h1("Title", class_name="text-lg")

@component
def Page():
    return h.div(h(Header))
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "function Header" in page_tsx
    assert "<Header" in page_tsx


def test_compile_with_props_and_import(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "components" / "card.py",
        """
from nestipy.web import component, props, h, js

@props
class CardProps:
    title: str
    active: bool = False

@component
def Card(props: CardProps):
    return h.div(h.h2(js("props.title")), class_name="card")
""".strip(),
    )

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h
from components.card import Card

@component
def Page():
    return h.div(Card(title="Hello"))
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "import { Card }" in page_tsx
    assert "<Card" in page_tsx

    card_tsx = (
        out_dir / "src" / "components" / "components" / "card.tsx"
    ).read_text(encoding="utf-8")
    assert "interface CardProps" in card_tsx
    assert "export function Card(props: CardProps): JSX.Element" in card_tsx


def test_vite_proxy_config(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    return h.div("Proxy")
""".strip(),
    )

    config = WebConfig(
        app_dir=str(app_dir),
        out_dir=str(out_dir),
        proxy="http://127.0.0.1:8001",
        proxy_paths=["/_actions", "/_router"],
    )
    compile_app(config, root=str(tmp_path))

    vite_config = (out_dir / "vite.config.ts").read_text(encoding="utf-8")
    assert "server" in vite_config
    assert "/_actions" in vite_config
    assert "127.0.0.1:8001" in vite_config


def test_compile_hooks_and_context(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import (
    component,
    h,
    use_state,
    use_effect,
    use_context,
    use_callback,
    use_memo,
    create_context,
)

AppContext = create_context("default")

@component
def Page():
    count, set_count = use_state(0)
    value = use_context(AppContext)

    def bump():
        set_count(count + 1)

    def label():
        return f"Count: {count}"

    handler = use_callback(bump, deps=[count])
    memo_label = use_memo(label, deps=[count])
    use_effect(bump, deps=[count])
    return h.div(memo_label)
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "import React from 'react';" in page_tsx
    assert "export const AppContext = React.createContext(\"default\");" in page_tsx
    assert "const [count, setCount] = React.useState(0);" in page_tsx
    assert "const value = React.useContext(AppContext);" in page_tsx
    assert "const bump = () =>" in page_tsx
    assert "setCount(" in page_tsx
    assert "const label = () =>" in page_tsx
    assert "const handler = React.useCallback(bump, [count]);" in page_tsx
    assert "const memoLabel = React.useMemo(label, [count]);" in page_tsx
    assert "React.useEffect(bump, [count]);" in page_tsx
    assert "{memoLabel}" in page_tsx


def test_compile_list_comprehension_and_conditional(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    items = [\"A\", \"B\"]
    show = True
    return h.div(
        h.ul([h.li(item) for item in items]),
        h.p(\"Shown\") if show else h.p(\"Hidden\"),
    )
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "].map" in page_tsx
    assert "show ? " in page_tsx


def test_compile_statement_if_and_for(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    items = [\"A\", \"B\"]
    show = True
    labels = []
    for item in items:
        labels.append(h.li(item))
    if show:
        message = h.p(\"Shown\")
    else:
        message = h.p(\"Hidden\")
    return h.div(h.ul(labels), message)
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "].map" in page_tsx
    assert "show ? " in page_tsx


def test_compile_if_multi_statement_branch(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    show = True
    if show:
        label = "Shown"
        message = h.p(label)
    else:
        label = "Hidden"
        message = h.p(label)
    return h.div(message)
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "show ? " in page_tsx


def test_compile_nested_for_loop(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    groups = [{\"items\": [\"A\", \"B\"]}]
    rows = []
    for group in groups:
        for item in group[\"items\"]:
            rows.append(h.li(item))
    return h.ul(rows)
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "group[\"items\"].map" in page_tsx


def test_layout_import_prefers_local(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "layout.py",
        """
from nestipy.web import component, h, Slot, create_context

ThemeContext = create_context("root")

@component
def Layout():
    return h.div(h(Slot))
""".strip(),
    )

    _write(
        app_dir / "api" / "layout.py",
        """
from nestipy.web import component, h, Slot, create_context

ThemeContext = create_context("local")

@component
def Layout():
    return h.div(h(Slot))
""".strip(),
    )

    _write(
        app_dir / "api" / "page.py",
        """
from nestipy.web import component, h
from layout import ThemeContext

@component
def Page():
    return h.div(ThemeContext, class_name="p-2")
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "api" / "page.tsx").read_text(
        encoding="utf-8"
    )
    assert "components/api/layout" in page_tsx
