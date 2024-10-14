from typing import Callable, Union, Type, Any

from .context_container import RequestContextContainer

TypeAnnotatedCallable = Callable[
    [str, Union[str, None], Type, RequestContextContainer], Any
]


class ParamAnnotation:
    def __init__(
        self,
        callback: TypeAnnotatedCallable,
        key: str,
        token: Union[str | Any, None] = None,
    ):
        self.key: Union[str, None] = key
        self.token: Union[str | Any, None] = token
        self.callback = callback
