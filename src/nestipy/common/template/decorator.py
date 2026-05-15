from typing import Any, Callable

from nestipy.metadata import Reflector

from .meta import TemplateKey


def Render(template: str) -> Callable[[Callable], Any]:
    """
    Args:
        template(str):

    Returns:
        callable(Callable): A callable decorator
    """

    def wrapper(method: Callable) -> Callable:
        Reflector.set_metadata(method, TemplateKey.MetaRender, template)
        return method

    return wrapper
