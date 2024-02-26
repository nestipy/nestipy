from typing import Callable

from nestipy.common.http_method import HttpMethod
from nestipy.core.utils import Utils


class Route:
    def __init__(self, method: HttpMethod, path='/', **kwargs):
        self.path = Utils.string_to_url_path(path)
        self.method = method
        self.kwargs = kwargs

    def __call__(self, func: Callable):
        setattr(func, "method__", self.method)
        setattr(func, "path__", self.path)
        setattr(func, "handler__", True)
        setattr(func, "kwargs__", self.kwargs)
        return func


class Get(Route):
    def __init__(self, path='/'):
        super().__init__(HttpMethod.GET, path)


class Post(Route):
    def __init__(self, path='/', **kwargs):
        super().__init__(HttpMethod.POST, path, **kwargs)


class Put(Route):
    def __init__(self, path='/', **kwargs):
        super().__init__(HttpMethod.PUT, path, **kwargs)


class Patch(Route):
    def __init__(self, path='/', **kwargs):
        super().__init__(HttpMethod.PATCH, path, **kwargs)


class Delete(Route):
    def __init__(self, path='/', **kwargs):
        super().__init__(HttpMethod.DELETE, path, **kwargs)
