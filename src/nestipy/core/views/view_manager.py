from __future__ import annotations

from typing import Literal, Union

from nestipy.common.template import TemplateEngine, TemplateKey
from nestipy.core.template import MinimalJinjaTemplateEngine


class ViewManager:
    """Manage static assets and template rendering configuration."""

    def __init__(self, http_adapter: object) -> None:
        self._http_adapter = http_adapter

    def use_static_assets(self, assets_path: str, url: str = "/static", *args, **kwargs) -> None:
        self._http_adapter.static(f"/{url.strip('/')}", assets_path, *args, **kwargs)

    def set_base_view_dir(self, view_dir: str) -> None:
        self._http_adapter.set(TemplateKey.MetaBaseView, view_dir)
        self._setup_template_engine(view_dir)

    def set_view_engine(self, engine: Union[Literal["minijinja"], TemplateEngine]) -> None:
        if isinstance(engine, TemplateEngine):
            self._http_adapter.set(TemplateKey.MetaEngine, engine)
        else:
            # TODO: add more template engines (e.g., jinja2)
            pass

    def _setup_template_engine(self, view_dir: str) -> None:
        engine = MinimalJinjaTemplateEngine(template_dir=view_dir)
        self._http_adapter.set(TemplateKey.MetaEngine, engine)

    def get_template_engine(self) -> TemplateEngine:
        engine: TemplateEngine | None = self._http_adapter.get_template_engine()
        if engine is None:
            raise Exception("Template engine not configured")
        return engine
