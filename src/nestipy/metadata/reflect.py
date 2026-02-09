from typing import Any, Union, Type, Callable


class Reflect:
    """
    Utility class for storing and retrieving metadata on objects (classes, methods, functions).
    Uses a special attribute `__reflect__metadata__` to store metadata as a dictionary.
    """

    metadata: str = "__reflect__metadata__"

    @classmethod
    def set_metadata(cls, obj: Union[Type, object, Callable], key: str, value: Any):
        """
        Store metadata on an object.
        :param obj: The target object to store metadata on.
        :param key: The metadata key.
        :param value: The metadata value.
        """
        meta: dict[str, Any] = getattr(obj, cls.metadata, {})
        meta[key] = value
        setattr(obj, cls.metadata, meta)

    @classmethod
    def get_metadata(
        cls, obj: Union[Type, object, Callable], key: str, default: Any = None
    ):
        """
        Retrieve metadata from an object.
        :param obj: The object to retrieve metadata from.
        :param key: The metadata key.
        :param default: Default value to return if key is not found.
        :return: The metadata value or default.
        """
        meta: dict[str, Any] = getattr(obj, cls.metadata, {})
        if key not in meta.keys():
            return default
        return meta[key]

    @classmethod
    def get(
        cls,
        obj: Union[Type, object, Callable],
    ):
        """
        Get all metadata stored on an object.
        :param obj: The target object.
        :return: A dictionary containing all metadata.
        """
        return getattr(obj, cls.metadata, {})
