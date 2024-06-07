from typing import Callable, Any

from nestipy.metadata import Reflect
from .meta import TemplateKey


def Render(template: str) -> Callable[[Callable], Any]:
    """
    Args:
        template(str):

    Returns:
        callable(Callable): A callable decorator
    """

    def wrapper(method: Callable) -> Callable:
        Reflect.set_metadata(method, TemplateKey.MetaRender, template)
        return method

    return wrapper
