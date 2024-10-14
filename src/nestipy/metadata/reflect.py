from typing import Any, Union, Type, Callable


class Reflect:
    metadata: str = "__reflect__metadata__"

    @classmethod
    def set_metadata(cls, obj: Union[Type, object, Callable], key: str, value: Any):
        meta: dict[str, Any] = getattr(obj, cls.metadata, {})
        meta[key] = value
        setattr(obj, cls.metadata, meta)

    @classmethod
    def get_metadata(
        cls, obj: Union[Type, object, Callable], key: str, default: Any = None
    ):
        meta: dict[str, Any] = getattr(obj, cls.metadata, {})
        if key not in meta.keys():
            return default
        return meta[key]

    @classmethod
    def get(
        cls,
        obj: Union[Type, object, Callable],
    ):
        return getattr(obj, cls.metadata, {})
