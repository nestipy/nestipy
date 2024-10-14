from typing import get_args, Any, Type, cast

from .dependency import TypeAnnotated, Default


class ContainerHelper:
    @classmethod
    def get_type_from_annotation(cls, annotation: Any) -> tuple[Type, TypeAnnotated]:
        args: tuple = get_args(annotation)
        if len(args) == 2:
            return cast(tuple[Type, TypeAnnotated], args)
        else:
            return annotation, Default()

    @classmethod
    def get_value_from_dict(cls, values: dict, key: str, default=None):
        return values.get(key) or default
