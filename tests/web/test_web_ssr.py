from __future__ import annotations

import json
from pathlib import Path

from nestipy.web import WebConfig
from nestipy.web.compiler import compile_app


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def test_compile_ssr_routes_written(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
__ssr__ = True

from nestipy.web import component, h

@component
def Page():
    return h.div("Hello")
        """,
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    ssr_routes = out_dir / "public" / "ssr-routes.json"
    assert ssr_routes.exists()
    payload = json.loads(ssr_routes.read_text(encoding="utf-8"))
    assert payload["routes"] == [{"path": "/", "ssr": True}]

    entry_server = out_dir / "src" / "entry-server.tsx"
    assert entry_server.exists()
    assert "createMemoryRouter" in entry_server.read_text(encoding="utf-8")


def test_compile_ssr_routes_disabled(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
__ssr__ = False

from nestipy.web import component, h

@component
def Page():
    return h.div("Hello")
        """,
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    ssr_routes = out_dir / "public" / "ssr-routes.json"
    assert ssr_routes.exists()
    payload = json.loads(ssr_routes.read_text(encoding="utf-8"))
    assert payload["routes"] == [{"path": "/", "ssr": False}]


def test_compile_ssr_routes_missing(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    out_dir = tmp_path / "web"

    _write(
        app_dir / "page.py",
        """
from nestipy.web import component, h

@component
def Page():
    return h.div("Hello")
        """,
    )

    config = WebConfig(app_dir=str(app_dir), out_dir=str(out_dir))
    compile_app(config, root=str(tmp_path))

    ssr_routes = out_dir / "public" / "ssr-routes.json"
    assert not ssr_routes.exists()
