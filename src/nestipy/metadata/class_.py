from typing import Callable, Type, Union, Optional

from .module import ModuleMetadata
from .reflect import Reflect


class ClassMetadata:
    Metadata = "__dependency_metadata__"
    _global_providers: list = []
    _module = None

    def __init__(self, module: Callable, global_providers: Optional[list] = None):
        self._module = module
        self._global_providers = global_providers or []

    def get_module(self):
        return self._module

    def get_global_providers(self):
        return self._global_providers

    def get_service_providers(self, module: Union[Type, None] = None):
        providers: list = Reflect.get_metadata(
            module or self._module, ModuleMetadata.Providers, []
        )
        import_providers_form_exports: list = []
        # Only not a root module need to get import_providers to share
        # if not Reflect.get_metadata(self._module, ModuleMetadata.Root, False):
        for im in Reflect.get_metadata(
            module or self._module, ModuleMetadata.Imports, []
        ):
            exports: list = Reflect.get_metadata(
                im.module if hasattr(im, "module") else im, ModuleMetadata.Exports, []
            )
            # check if dynamic module
            # if hasattr(im, 'module') and hasattr(im, 'exports'):
            #     exports = getattr(im, 'exports', [])
            for export in exports:
                # For module re-exporting
                is_module: bool = Reflect.get_metadata(
                    export, ModuleMetadata.Module, False
                )
                if is_module:
                    import_providers_form_exports = (
                        import_providers_form_exports
                        + Reflect.get_metadata(export, ModuleMetadata.Providers, [])
                    )
                else:
                    import_providers_form_exports.append(export)
        return providers, import_providers_form_exports
