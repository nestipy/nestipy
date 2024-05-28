from typing import TypeVar, Callable, Union, Type, Any

from .context_container import RequestContextContainer

TypeAnnotatedCallable = Callable[[str, Union[str, None], Type, RequestContextContainer], Any]


class ParamAnnotation:
    def __init__(self, callback: TypeAnnotatedCallable, key: str, token: Union[str, None] = None):
        self.key: Union[str, None] = key
        self.token: Union[str, None] = token
        self.callback = callback
