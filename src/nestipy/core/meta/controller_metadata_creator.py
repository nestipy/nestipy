from typing import Type

from nestipy.metadata import ModuleMetadata, Reflect

from .metadata_creator import MetadataCreator


class ControllerMetadataCreator(MetadataCreator):
    def _type(self) -> Type["MetadataCreator"]:
        return ControllerMetadataCreator

    def _extract(self) -> list:
        return Reflect.get_metadata(self.module, ModuleMetadata.Controllers, [])
