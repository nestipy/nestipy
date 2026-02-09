from typing import Callable, Union, Type, Any

from .context_container import RequestContextContainer

TypeAnnotatedCallable = Callable[
    [str, Union[str, None], Type, RequestContextContainer], Any
]


class ParamAnnotation:
    """
    Metadata class for defining custom parameter annotations.
    Used for extracting values from the execution context (e.g., @Body, @Param).
    """

    def __init__(
        self,
        callback: TypeAnnotatedCallable,
        key: Union[str, None],
        token: Union[str | Any, None] = None,
        pipes: Union[list, None] = None,
    ):
        """
        Initialize ParamAnnotation.
        :param callback: The function to call for resolving the dependency value.
        :param key: The CtxDepKey identifier for the dependency type.
        :param token: Optional token for specific items (e.g., parameter name).
        :param pipes: Optional list of pipes to apply for this parameter.
        """
        self.key: Union[str, None] = key
        self.token: Union[str | Any, None] = token
        self.callback = callback
        self.pipes: list = pipes or []
