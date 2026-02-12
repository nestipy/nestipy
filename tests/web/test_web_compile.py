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
    return h("div", {"className": "p-4"}, "Hello")
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
    return h("div", {"className": "layout"},
        h("main", {}, h(Slot)),
    )
""".strip(),
    )

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    return h("section", {}, "Content")
""".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / "src" / "pages" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "RootLayout" in page_tsx
    assert "ReactNode" in page_tsx


def test_compile_with_nested_component(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        \"\"\"
from nestipy.web import component, h

@component
def Header():
    return h(\"h1\", {\"className\": \"text-lg\"}, \"Title\")

@component
def Page():
    return h(\"div\", {}, h(Header))
\"\"\".strip(),
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    page_tsx = (out_dir / \"src\" / \"pages\" / \"index.tsx\").read_text(
        encoding=\"utf-8\"
    )
    assert \"function Header\" in page_tsx
    assert \"<Header\" in page_tsx
