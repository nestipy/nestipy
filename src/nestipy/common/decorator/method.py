from typing import Callable, Literal, Union

from nestipy.metadata import Reflect, RouteKey

HTTPMethod = Literal[
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "ALL", "ANY"
]


class Route:
    def __init__(
        self, path: str = "", method: Union[list[HTTPMethod], None] = None, **kwargs
    ):
        if method is None:
            method = ["GET"]
        self.path = path
        self.kwargs = kwargs
        self.method = method

    def __call__(self, handler: Callable):
        # put path and kwargs in controller handler
        Reflect.set_metadata(handler, RouteKey.path, self.path)
        Reflect.set_metadata(handler, RouteKey.kwargs, self.kwargs)
        Reflect.set_metadata(handler, RouteKey.method, self.method)
        return handler


def Get(path: str = "", **kwargs):
    return Route(path=path, method=["GET"], **kwargs)


def Post(path: str = "", **kwargs):
    return Route(path=path, method=["POST"], **kwargs)


def Put(path: str = "", **kwargs):
    return Route(path=path, method=["PUT"], **kwargs)


def Patch(path: str = "", **kwargs):
    return Route(path=path, method=["PATCH"], **kwargs)


def Delete(path: str = "", **kwargs):
    return Route(path=path, method=["DELETE"], **kwargs)
