from typing import Union, Callable, Any, TYPE_CHECKING

from nestipy.metadata import Reflect

from nestipy.common.template import TemplateEngine, TemplateKey
from .minimal_jinja import MinimalJinjaTemplateEngine

if TYPE_CHECKING:
    from nestipy.core.adapter.http_adapter import HttpAdapter


class TemplateRendererProcessor:
    def __init__(self, adapter: "HttpAdapter"):
        self.template = None
        self.adapter = adapter
        self.template_engine = None
        self.context = {}

    def can_process(self, method: Callable, context: Any) -> bool:
        self.template_engine: Union[TemplateEngine, None] = self.adapter.get_state(
            TemplateKey.MetaEngine
        )
        self.template = Reflect.get_metadata(method, TemplateKey.MetaRender, None)
        self.context = context
        if self.template_engine is None:
            return False
            # raise HttpException(HttpStatus.INTERNAL_SERVER_ERROR, 'Template engine not configured')
        if self.template is None or not isinstance(context, dict):
            return False
        else:
            return True

    def render(self) -> Union[str, None]:
        template_engine: Union[TemplateEngine, None] = self.adapter.get_state(
            TemplateKey.MetaEngine
        )
        if template_engine is None:
            return None
        else:
            return template_engine.render(self.template, self.context)


__all__ = ["MinimalJinjaTemplateEngine", "TemplateRendererProcessor"]
