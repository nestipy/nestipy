from typing import Union, Callable, Any, TYPE_CHECKING

from .engine import TemplateEngine
from .minimal_jinja import MinimalJinjaTemplateEngine
from .. import Reflect
from ..exception.http import HttpException
from ..exception.status import HttpStatus

if TYPE_CHECKING:
    from ...core.adapter.http_adapter import HttpAdapter

TEMPLATE_RENDER_KEY = "__template__render__"
TEMPLATE_ENGINE_KEY = "__template__engine__"


def Render(template: str):
    def wrapper(method: Callable):
        Reflect.set_metadata(method, TEMPLATE_RENDER_KEY, template)
        return method

    return wrapper


class TemplateRendererProcessor:
    def __init__(self, adapter: "HttpAdapter"):
        self.template = None
        self.adapter = adapter
        self.template_engine = None
        self.context = {}

    def can_process(self, method: Callable, context: Any) -> bool:
        self.template_engine: Union[TemplateEngine, None] = self.adapter.get_state(TEMPLATE_ENGINE_KEY)
        self.template = Reflect.get_metadata(method, TEMPLATE_RENDER_KEY, None)
        self.context = context
        if self.template_engine is None:
            return False
            # raise HttpException(HttpStatus.INTERNAL_SERVER_ERROR, 'Template engine not configured')
        if self.template is None or not isinstance(context, dict):
            return False
        else:
            return True

    def render(self) -> Union[str, None]:
        template_engine: Union[TemplateEngine, None] = self.adapter.get_state(TEMPLATE_ENGINE_KEY)
        if template_engine is None:
            return None
        else:
            return template_engine.render(self.template, self.context)


__all__ = [
    "TemplateEngine",
    "MinimalJinjaTemplateEngine",
    "TEMPLATE_ENGINE_KEY",
    "TEMPLATE_RENDER_KEY",
    "Render",
    "TemplateRendererProcessor"
]
