from typing import Type

from .metadata_creator import MetadataCreator
from nestipy.common.metadata.module import ModuleMetadata
from nestipy.common.metadata.reflect import Reflect


class ControllerMetadataCreator(MetadataCreator):
    def _type(self) -> Type["MetadataCreator"]:
        return ControllerMetadataCreator

    def _extract(self) -> list:
        return Reflect.get_metadata(self.module, ModuleMetadata.Controllers, [])
