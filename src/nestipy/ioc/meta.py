from typing import get_args, Any, Type, cast

from .dependency import TypeAnnotated, Instance


class ContainerHelper:

    @classmethod
    def get_type_from_annotation(cls, annotation: Any) -> tuple[Type, TypeAnnotated]:
        args: tuple = get_args(annotation)
        if len(args) == 2:
            return cast(tuple[Type, TypeAnnotated], args)
        else:
            return annotation, Instance()

    @classmethod
    def get_value_from_dict(cls, values: dict, key: str, default=None):
        if key in values.keys():
            return values[key]
        else:
            return default
