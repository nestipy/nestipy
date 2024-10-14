from abc import ABC, abstractmethod
from typing import Type, Union

from nestipy.common.utils import uniq_list
from nestipy.dynamic_module import DynamicModule
from nestipy.ioc import NestipyContainer
from nestipy.metadata import ClassMetadata, ModuleMetadata, Reflect


class MetadataCreator(ABC):
    def __init__(self, module, global_data=None, is_root=False):
        self.module = self._dynamic_module_to_module(module)
        self.is_root = is_root
        self.global_data = global_data or []

    @abstractmethod
    def _extract(self) -> list:
        pass

    @abstractmethod
    def _type(self) -> Type["MetadataCreator"]:
        pass

    def extract_providers(self) -> list:
        return uniq_list(
            Reflect.get_metadata(self.module, ModuleMetadata.Providers, [])
        )

    def _put_dependency_metadata(self) -> None:
        data = self._extract()
        for p in data:
            global_data = self.extract_providers() if self.is_root else self.global_data
            # only p that have not metadata
            if not hasattr(p, ClassMetadata.Metadata):
                Reflect.set_metadata(
                    p,
                    ClassMetadata.Metadata,
                    ClassMetadata(self.module, global_providers=global_data),
                )

    def _extract_import(self) -> list:
        """
        Extract module imported in Module
        :return: list
        """
        return uniq_list(
            [
                self._dynamic_module_to_module(m)
                for m in Reflect.get_metadata(self.module, ModuleMetadata.Imports, [])
            ]
        )

    @classmethod
    def _dynamic_module_to_module(cls, im: Union[Type, object]):
        if isinstance(im, DynamicModule):
            Reflect.set_metadata(im.module, ModuleMetadata.Providers, im.providers)
            Reflect.set_metadata(im.module, ModuleMetadata.Controllers, im.controllers)
            Reflect.set_metadata(im.module, ModuleMetadata.Imports, im.imports)
            Reflect.set_metadata(im.module, ModuleMetadata.Exports, im.exports)
            Reflect.set_metadata(im.module, ModuleMetadata.Global, im.is_global)
            NestipyContainer.get_instance().add_singleton(im.module)
            return im.module
        else:
            return im

    def create(self) -> None:
        """
        Compile is about put module parent to the dependency metadata of a provider or controller
        :return:
        """
        if self.is_root:
            Reflect.set_metadata(self.module, ModuleMetadata.Root, True)
            self.global_data = self.extract_providers()
            # compile global first
            imports = self._extract_import()
            not_global_module = []
            for im in imports:
                if not Reflect.get_metadata(im, ModuleMetadata.Global, False):
                    not_global_module.append(im)
                else:
                    self._type()(im, global_data=self.global_data).create()
                    import_providers_form_exports = []
                    for export in Reflect.get_metadata(im, ModuleMetadata.Exports, []):
                        # For module re-exporting
                        is_module: bool = Reflect.get_metadata(
                            export, ModuleMetadata.Module, False
                        )
                        if is_module:
                            import_providers_form_exports = (
                                import_providers_form_exports
                                + Reflect.get_metadata(
                                    export, ModuleMetadata.Providers, []
                                )
                            )
                        else:
                            import_providers_form_exports.append(export)
                    self.global_data = self.global_data + import_providers_form_exports

            # compile non global after
            for im in not_global_module:
                self._type()(im, global_data=self.global_data).create()
            self._put_dependency_metadata()
        else:
            self._put_dependency_metadata()
