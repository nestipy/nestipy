from typing import Type

from nestipy.metadata import ModuleMetadata, Reflect

from .metadata_creator import MetadataCreator


class ProviderMetadataCreator(MetadataCreator):
    def _type(self) -> Type["MetadataCreator"]:
        return ProviderMetadataCreator

    def _extract(self) -> list:
        return Reflect.get_metadata(self.module, ModuleMetadata.Providers, [])
