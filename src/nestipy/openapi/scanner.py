import typing

from nestipy.common.metadata.reflect import Reflect


class OpenApiScanner:

    @classmethod
    def scan(cls, obj):
        deps: dict = {}
        meta = Reflect.get(obj)
        for key, value in meta.items():
            if typing.cast(str, key).startswith('__openapi__'):
                openapi_key = typing.cast(str, key).replace('__openapi__', '')
                deps[openapi_key] = value
        return deps
