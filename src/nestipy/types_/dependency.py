from typing import Union, TypeVar, Tuple, Any, Annotated

from nestipy.common.metadata.dependency import CtxDepKey

T = TypeVar('T')


class Annotation:
    def __init__(self, metadata=None, *args):
        self.metadata = metadata
        self.args = args


class DependencyMeta:

    def __init__(self, metadata=None):
        self.metadata = metadata

    def __getitem__(self, params: Union[T, Tuple[Union[T, Any]]]) -> Annotated[T, Any]:
        if isinstance(params, tuple):
            if len(params) >= 2:
                type_annotation, *metadata = params
                return Annotated[type_annotation, Annotation(self.metadata, metadata)]
            elif len(params) == 1:
                return Annotated[params[0], Annotation(self.metadata)]
            else:
                raise ValueError("Inject[type, metadata] syntax is required")
        else:
            return Annotated[params, Annotation(self.metadata)]


Inject = DependencyMeta(CtxDepKey.Service)
Req = DependencyMeta(CtxDepKey.Request)
Res = DependencyMeta(CtxDepKey.Response)
Session = DependencyMeta(CtxDepKey.Session)
Query = DependencyMeta(CtxDepKey.Query)
Body = DependencyMeta(CtxDepKey.Body)
Params = DependencyMeta(CtxDepKey.Params)
Args = DependencyMeta(CtxDepKey.Args)
Context = DependencyMeta(CtxDepKey.Context)
Files = DependencyMeta(CtxDepKey.Files)
SocketServer = DependencyMeta(CtxDepKey.Service)
SocketClient = DependencyMeta(CtxDepKey.SocketClient)
SocketData = DependencyMeta(CtxDepKey.SocketData)
