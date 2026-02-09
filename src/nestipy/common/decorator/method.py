from typing import Callable, Literal, Union

from nestipy.metadata import Reflect, RouteKey

HTTPMethod = Literal[
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "ALL", "ANY"
]


class Route:
    """
    Decorator that marks a method of a controller as a request handler.
    """

    def __init__(
        self, path: str = "", method: Union[list[HTTPMethod], None] = None, **kwargs
    ):
        """
        Initialize the Route decorator.
        :param path: The path for the route.
        :param method: List of HTTP methods supported by the route.
        :param kwargs: Additional metadata for the route.
        """
        if method is None:
            method = ["GET"]
        self.path = path
        self.kwargs = kwargs
        self.method = method

    def __call__(self, handler: Callable):
        """
        Set route metadata on the handler function.
        :param handler: The controller method to be decorated.
        :return: The decorated handler.
        """
        # put path and kwargs in controller handler
        Reflect.set_metadata(handler, RouteKey.path, self.path)
        Reflect.set_metadata(handler, RouteKey.kwargs, self.kwargs)
        Reflect.set_metadata(handler, RouteKey.method, self.method)
        return handler


def Get(path: str = "", **kwargs):
    """
    Decorator that marks a method as a GET request handler.
    :param path: The path for the route.
    :param kwargs: Additional metadata for the route.
    """
    return Route(path=path, method=["GET"], **kwargs)


def Post(path: str = "", **kwargs):
    """
    Decorator that marks a method as a POST request handler.
    :param path: The path for the route.
    :param kwargs: Additional metadata for the route.
    """
    return Route(path=path, method=["POST"], **kwargs)


def Put(path: str = "", **kwargs):
    """
    Decorator that marks a method as a PUT request handler.
    :param path: The path for the route.
    :param kwargs: Additional metadata for the route.
    """
    return Route(path=path, method=["PUT"], **kwargs)


def Patch(path: str = "", **kwargs):
    """
    Decorator that marks a method as a PATCH request handler.
    :param path: The path for the route.
    :param kwargs: Additional metadata for the route.
    """
    return Route(path=path, method=["PATCH"], **kwargs)


def Delete(path: str = "", **kwargs):
    """
    Decorator that marks a method as a DELETE request handler.
    :param path: The path for the route.
    :param kwargs: Additional metadata for the route.
    """
    return Route(path=path, method=["DELETE"], **kwargs)
