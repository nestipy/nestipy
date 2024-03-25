from typing import Union, TypeVar, Tuple, Any, Annotated

from nestipy.common.metadata.dependency import DependencyKey

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


Inject = DependencyMeta(DependencyKey.Service)
Req = DependencyMeta(DependencyKey.Request)
Res = DependencyMeta(DependencyKey.Response)
Session = DependencyMeta(DependencyKey.Session)
Query = DependencyMeta(DependencyKey.Query)
Body = DependencyMeta(DependencyKey.Body)
Params = DependencyMeta(DependencyKey.Params)
Args = DependencyMeta(DependencyKey.Args)
Context = DependencyMeta(DependencyKey.Context)
Files = DependencyMeta(DependencyKey.Files)
WebSocketServer = DependencyMeta(DependencyKey.WebSocketServer)
