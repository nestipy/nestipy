from typing import get_args, Any

from nestipy.metadata import ProviderToken

from .annotation import Annotation


class ContainerHelper:

    @classmethod
    def get_type_from_annotation(cls, annotation: Any) -> tuple[Any, Annotation]:
        args: tuple = get_args(annotation)
        # check if key is from provide(ModuleProviderDict)
        if len(args) == 2:
            arg1, annot = args
            if isinstance(arg1, ProviderToken):
                return args[0].key, args[1]
            return args[0], args[1]
        else:
            if isinstance(annotation, ProviderToken):
                return annotation.key, Annotation()
            return annotation, Annotation()

    @classmethod
    def get_value_from_dict(cls, values: dict, key: str, default=None):
        if key in values.keys():
            return values[key]
        else:
            return default
