from typing import Callable

from nestipy.metadata import Reflect

from .meta import TemplateKey


def Render(template: str):
    def wrapper(method: Callable):
        Reflect.set_metadata(method, TemplateKey.MetaRender, template)
        return method

    return wrapper
