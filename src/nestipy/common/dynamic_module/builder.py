import uuid
from dataclasses import dataclass
from typing import TypeVar, Generic, Optional, Any, Callable

from nestipy.common.metadata.module import ModuleMetadata
from nestipy.common.metadata.reflect import Reflect
from nestipy.common.provider import ModuleProviderDict

T = TypeVar('T')


@dataclass
class DynamicModule:
    module: Any
    exports: list = None
    imports: list = None
    providers: list = None
    controllers: list = None
    is_global: bool = False


class ConfigurableModuleBuilder(Generic[T]):
    def __init__(self):
        self.method_name = 'register'

    def set_method(self, name: str):
        self.method_name = name
        return self

    @classmethod
    def _create_dynamic_module(cls, obj: Any, provider: list) -> DynamicModule:
        return DynamicModule(
            obj,
            providers=provider + Reflect.get_metadata(obj, ModuleMetadata.Providers, []),
            exports=Reflect.get_metadata(obj, ModuleMetadata.Exports, []),
            imports=Reflect.get_metadata(obj, ModuleMetadata.Imports, []),
            controllers=Reflect.get_metadata(obj, ModuleMetadata.Controllers, [])
        )

    def build(self):
        MODULE_OPTION_TOKEN = f"{uuid.uuid4().hex}_TOKEN"

        def register(cls_: Any, options: Optional[T]) -> DynamicModule:
            provider = ModuleProviderDict(
                token=MODULE_OPTION_TOKEN,
                value=options
            )
            return self._create_dynamic_module(cls_, [provider])

        def register_async(cls_: Any, factory: Callable[..., T]) -> DynamicModule:
            provider = ModuleProviderDict(
                token=MODULE_OPTION_TOKEN,
                factory=factory
            )
            return self._create_dynamic_module(cls_, [provider])

        cls = type('ConfigurableModuleClass', (object,), {
            self.method_name: classmethod(register),
            f"{self.method_name}_async": classmethod(register_async)
        })
        return cls, MODULE_OPTION_TOKEN
