from typing import Type

from nestipy.metadata import ModuleMetadata, Reflector

from .metadata_creator import MetadataCreator


class ControllerMetadataCreator(MetadataCreator):
    def _type(self) -> Type["MetadataCreator"]:
        return ControllerMetadataCreator

    def _extract(self) -> list:
        return Reflector.get_metadata(self.module, ModuleMetadata.Controllers, [])
