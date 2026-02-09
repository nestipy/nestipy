from typing import get_args, get_origin, Any, Type, cast, Annotated

from .dependency import TypeAnnotated, Default


class ContainerHelper:
    @classmethod
    def get_type_from_annotation(cls, annotation: Any) -> tuple[Type, TypeAnnotated]:
        if isinstance(annotation, TypeAnnotated):
            return object, annotation
        if get_origin(annotation) is Annotated:
            args: tuple = get_args(annotation)
            if len(args) >= 2:
                base = args[0]
                dep = next(
                    (item for item in args[1:] if isinstance(item, TypeAnnotated)),
                    None,
                )
                if dep is not None:
                    return cast(Type, base), dep
        return annotation, Default()

    @classmethod
    def get_value_from_dict(cls, values: dict, key: str, default=None):
        return values.get(key) or default
