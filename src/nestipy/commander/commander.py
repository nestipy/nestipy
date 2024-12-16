import traceback
from typing import Type, Optional, cast

from nestipy.common import logger
from nestipy.common.utils import uniq_list
from nestipy.core.instance_loader import InstanceLoader
from nestipy.core.meta.controller_metadata_creator import ControllerMetadataCreator
from nestipy.core.meta.module_metadata_creator import ModuleMetadataCreator
from nestipy.core.meta.provider_metadata_creator import ProviderMetadataCreator
from nestipy.dynamic_module import DynamicModule
from nestipy.metadata import ModuleMetadata
from nestipy.metadata.reflect import Reflect
from .abstract import BaseCommand
from .meta import CommanderMeta


class NestipyCommander(object):
    _root_module: Optional[Type] = None

    def __init__(self):
        self.instance_loader = InstanceLoader()

    @classmethod
    def _get_modules(cls, module: Type) -> list[Type]:
        modules: list[Type] = [module]
        for m in Reflect.get_metadata(module, ModuleMetadata.Imports, []):
            if isinstance(m, DynamicModule):
                modules.append(m.module)
            else:
                modules.append(m)
        return uniq_list(modules)

    def init(self, root_module: Type):
        self._root_module = root_module
        self._set_metadata()

    async def run(self, command_name: str, context: dict):
        try:
            modules = self._get_modules(self._root_module)
            await self.instance_loader.create_instances(
                modules
            )
            commands: dict[str, BaseCommand] = {}
            for c in self.instance_loader.discover.get_all_provider():
                meta: Optional[dict[str]] = Reflect.get_metadata(c, CommanderMeta.Meta)
                if meta is not None and issubclass(c.__class__, BaseCommand):
                    commands.update({meta.get("name"): cast(BaseCommand, c)})

            command = commands.get(command_name, None)
            if command is not None:
                await command.run(context)
            else:
                logger.error(f"Command '{command_name}' not found ")
            await self.instance_loader.destroy()

        except Exception as e:
            _tb = traceback.format_exc()
            logger.error(e)
            logger.error(_tb)

    def _set_metadata(self):
        provider_metadata_maker = ProviderMetadataCreator(
            self._root_module, is_root=True
        )
        provider_metadata_maker.create()

        controller_metadata_maker = ControllerMetadataCreator(
            self._root_module, is_root=True
        )
        controller_metadata_maker.create()

        # optional
        module_metadata_maker = ModuleMetadataCreator(self._root_module)
        module_metadata_maker.create()
