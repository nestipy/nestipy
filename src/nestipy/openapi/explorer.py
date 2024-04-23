import typing

from nestipy_metadata import Reflect


class OpenApiExplorer:

    @classmethod
    def explore(cls, obj):
        deps: dict = {}
        meta = Reflect.get(obj)
        for key, value in meta.items():
            if typing.cast(str, key).startswith('__openapi__'):
                openapi_key = typing.cast(str, key).replace('__openapi__', '')
                deps[openapi_key] = value
        return deps
