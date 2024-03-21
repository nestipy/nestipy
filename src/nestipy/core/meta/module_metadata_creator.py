from typing import Type

from nestipy.common.metadata.module import ModuleMetadata
from nestipy.common.metadata.reflect import Reflect
from .metadata_creator import MetadataCreator
from ...common.metadata.class_ import ClassMetadata


class ModuleMetadataCreator(MetadataCreator):
    def _extract(self) -> list:
        return Reflect.get_metadata(self.module, ModuleMetadata.Imports, [])

    def _type(self) -> Type["MetadataCreator"]:
        return ModuleMetadataCreator

    def create(self) -> None:
        imports = [self.module] + self._extract_import()
        for im in imports:
            Reflect.set_metadata(
                im,
                ClassMetadata.Metadata,
                ClassMetadata(
                    im,
                    global_providers=self.extract_providers()
                )
            )
