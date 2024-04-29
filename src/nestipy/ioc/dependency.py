from typing import Union, TypeVar, Tuple, Any, Annotated

from nestipy.metadata import CtxDepKey, ProviderToken

from .annotation import Annotation

T = TypeVar('T')


class _TypedDependency:

    def __init__(self, metadata=None):
        self.metadata = metadata

    def __getitem__(self, params: Union[str, T, Tuple[Union[T, Any]]]) -> Annotated[T, Annotation]:
        if isinstance(params, tuple):
            if len(params) >= 2:
                type_annotation, *metadata = params
                return Annotated[self._check_if_str(type_annotation), Annotation(self.metadata, metadata)]
            elif len(params) == 1:
                return Annotated[self._check_if_str(params[0]), Annotation(self.metadata)]
            else:
                raise ValueError("Inject[type, metadata] syntax is required")
        else:
            return Annotated[self._check_if_str(params), Annotation(self.metadata)]

    @classmethod
    def _check_if_str(cls, type_annotation: Any):
        if isinstance(type_annotation, str):
            return ProviderToken(type_annotation)
        return type_annotation


Inject = _TypedDependency(CtxDepKey.Service)
Req = _TypedDependency(CtxDepKey.Request)
Res = _TypedDependency(CtxDepKey.Response)
Session = _TypedDependency(CtxDepKey.Session)
Query = _TypedDependency(CtxDepKey.Query)
Body = _TypedDependency(CtxDepKey.Body)
Params = _TypedDependency(CtxDepKey.Params)
Args = _TypedDependency(CtxDepKey.Args)
Context = _TypedDependency(CtxDepKey.Context)
Files = _TypedDependency(CtxDepKey.Files)
SocketServer = _TypedDependency(CtxDepKey.Service)
SocketClient = _TypedDependency(CtxDepKey.SocketClient)
SocketData = _TypedDependency(CtxDepKey.SocketData)
