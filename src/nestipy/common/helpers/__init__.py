from typing import Type

from nestipy.ioc import ModuleProviderDict
from nestipy.metadata import Reflect, ClassMetadata, ModuleMetadata


class SpecialProviderExtractor:
    @classmethod
    def extract_special_providers(
        cls, module_class: Type, subclass: Type, key: str
    ) -> list[Type]:
        providers = []
        class_providers = Reflect.get_metadata(
            module_class, ModuleMetadata.Providers, []
        )
        metadata: ClassMetadata = Reflect.get_metadata(
            module_class, ClassMetadata.Metadata, None
        )
        if metadata is not None:
            class_providers += metadata.get_global_providers()
        for p in class_providers:
            if (
                isinstance(p, ModuleProviderDict)
                and isinstance(p.token, str)
                and p.token.startswith(key)
                and p.use_class is not None
            ):
                if issubclass(p.use_class, subclass):
                    providers.append(p.use_class)
        return providers
