from typing import Type

from nestipy.metadata import ModuleMetadata, Reflector

from .metadata_creator import MetadataCreator


class ProviderMetadataCreator(MetadataCreator):
    def _type(self) -> Type["MetadataCreator"]:
        return ProviderMetadataCreator

    def _extract(self) -> list:
        return Reflector.get_metadata(self.module, ModuleMetadata.Providers, [])
