from typing import Type

from nestipy.metadata import ClassMetadata, ModuleMetadata, Reflector

from .metadata_creator import MetadataCreator


class ModuleMetadataCreator(MetadataCreator):
    def _extract(self) -> list:
        return Reflector.get_metadata(self.module, ModuleMetadata.Imports, [])

    def _type(self) -> Type["MetadataCreator"]:
        return ModuleMetadataCreator

    def create(self) -> None:
        imports = [self.module] + self._extract_import()
        providers = self.extract_providers()
        for im in imports:
            Reflector.set_metadata(
                im,
                ClassMetadata.Metadata,
                ClassMetadata(im, global_providers=providers),
            )
