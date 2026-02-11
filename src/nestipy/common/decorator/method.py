from typing import Callable, Iterable, Literal, Optional, Union

from nestipy.metadata import Reflect, RouteKey
from nestipy.common.cache import CachePolicy

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


class Version:
    """
    Decorator that assigns a version to a controller or handler.
    """

    def __init__(self, *versions: Union[str, Iterable[str]]):
        flat: list[str] = []
        for version in versions:
            if isinstance(version, (list, tuple, set)):
                flat.extend([str(v) for v in version])
            else:
                flat.append(str(version))
        self.versions = [v for v in flat if v]

    def __call__(self, target: Callable):
        Reflect.set_metadata(target, RouteKey.version, self.versions or None)
        return target


class Cache:
    """
    Decorator that sets a cache policy for a controller or handler.
    """

    def __init__(
        self,
        policy: Optional[CachePolicy] = None,
        *,
        max_age: Optional[int] = None,
        s_maxage: Optional[int] = None,
        public: Optional[bool] = None,
        private: Optional[bool] = None,
        no_store: bool = False,
        no_cache: bool = False,
        must_revalidate: bool = False,
        stale_while_revalidate: Optional[int] = None,
        stale_if_error: Optional[int] = None,
        vary: Optional[Iterable[str]] = None,
        etag: Optional[str] = None,
        last_modified: Optional[str] = None,
    ):
        self.policy = policy or CachePolicy(
            max_age=max_age,
            s_maxage=s_maxage,
            public=public,
            private=private,
            no_store=no_store,
            no_cache=no_cache,
            must_revalidate=must_revalidate,
            stale_while_revalidate=stale_while_revalidate,
            stale_if_error=stale_if_error,
            vary=vary,
            etag=etag,
            last_modified=last_modified,
        )

    def __call__(self, target: Callable):
        Reflect.set_metadata(target, RouteKey.cache, self.policy)
        return target
