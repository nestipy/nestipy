from typing import Type

from nestipy.common import ModuleMetadata, ModuleProviderDict, Reflect


class SpecialProviderExtractor:

    @classmethod
    def extract_special_providers(
            cls,
            module_class: Type,
            subclass: Type,
            key: str
    ) -> list[Type]:
        providers = []
        for p in Reflect.get_metadata(module_class, ModuleMetadata.Providers, []):
            if isinstance(p, ModuleProviderDict) and p.token.startswith(key) and p.use_class is not None:
                if issubclass(p.use_class, subclass):
                    providers.append(p.use_class)
        return providers
