from typing import Callable, Type, Union, Optional, Any

from .module import ModuleMetadata
from .reflect import Reflect


class ClassMetadata:
    """
    Holds metadata about a class's relationship with its parent module and global providers.
    """
    Metadata = "__dependency_metadata__"
    _global_providers: list = []
    _module = None

    def __init__(self, module: Any, global_providers: Optional[list] = None):
        """
        Initialize ClassMetadata.
        :param module: The module class to which the target class belongs.
        :param global_providers: List of global providers available in the system.
        """
        self._module = module
        self._global_providers = global_providers or []

    def get_module(self):
        """
        Get the parent module.
        :return: The module class.
        """
        return self._module

    def get_global_providers(self):
        """
        Get global providers.
        :return: List of global providers.
        """
        return self._global_providers

    def get_service_providers(self, module: Union[Type, None] = None):
        """
        Retrieve all providers available to a service within a specific module context.
        This includes local providers and exported providers from imported modules.
        :param module: Optional module to use instead of the stored parent module.
        :return: A tuple of (local_providers, exported_import_providers).
        """
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
