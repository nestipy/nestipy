import typing

from nestipy.metadata import Reflect


class OpenApiExplorer:
    @classmethod
    def explore(cls, obj):
        deps: dict = {}
        schemas: dict = {}
        meta = Reflect.get(obj)
        for key, value in meta.items():
            if typing.cast(str, key).startswith("__openapi__"):
                openapi_key = typing.cast(str, key).replace("__openapi__", "")
                if openapi_key == "schemas":
                    schemas[openapi_key] = value
                else:
                    deps[openapi_key] = value

        return deps, schemas
