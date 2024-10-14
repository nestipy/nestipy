import uuid
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Any, Callable, Union, Type, Awaitable

from nestipy.ioc.provider import ModuleProviderDict
from nestipy.metadata import ModuleMetadata, Reflect

T = TypeVar("T")


@dataclass
class DynamicModule:
    module: Any
    exports: list = field(default_factory=lambda: [])
    imports: list = field(default_factory=lambda: [])
    providers: list = field(default_factory=lambda: [])
    controllers: list = field(default_factory=lambda: [])
    is_global: bool = False


class ConfigurableModuleBuilder(Generic[T]):
    def __init__(self):
        self._method_name = "register"
        self._extras: Union[dict[str, Any], None] = None
        self._extras_process_callback: Union[
            Callable[[DynamicModule, dict[str, Any]], None], None
        ] = None

    def set_extras(
        self,
        extras: dict[str, Any],
        extras_callback: Callable[[DynamicModule, dict[str, Any]], None],
    ):
        self._extras = extras
        self._extras_process_callback = extras_callback
        return self

    def set_method(self, name: str):
        self._method_name = name
        return self

    def _extra_return(self, dynamic_module: DynamicModule) -> DynamicModule:
        if self._extras is not None and self._extras_process_callback is not None:
            self._extras_process_callback(dynamic_module, self._extras)
        return dynamic_module

    def _create_dynamic_module(
        self, obj: Any, imports: list, provider: list
    ) -> DynamicModule:
        dynamic_module = DynamicModule(
            obj,
            providers=provider
            + Reflect.get_metadata(obj, ModuleMetadata.Providers, []),
            exports=Reflect.get_metadata(obj, ModuleMetadata.Exports, []),
            imports=imports + Reflect.get_metadata(obj, ModuleMetadata.Imports, []),
            controllers=Reflect.get_metadata(obj, ModuleMetadata.Controllers, []),
            is_global=Reflect.get_metadata(obj, ModuleMetadata.Global, False),
        )
        return self._extra_return(dynamic_module)

    def build(self) -> tuple[Type, str]:
        MODULE_OPTION_TOKEN = f"{uuid.uuid4().hex}_TOKEN"

        def register(
            cls_: Any, options: Optional[T], extras: Optional[dict] = None
        ) -> DynamicModule:
            if extras is not None:
                self._extras = extras
            provider = ModuleProviderDict(token=MODULE_OPTION_TOKEN, value=options)
            return self._create_dynamic_module(cls_, [], [provider])

        def register_async(
            cls_: Any,
            value: Optional[T] = None,
            factory: Optional[Callable[..., Union[Awaitable, Any]]] = None,
            existing: Optional[Union[Type, str]] = None,
            use_class: Optional[Type] = None,
            inject: Optional[list] = None,
            imports: Optional[list] = None,
            extras: Optional[dict] = None,
        ) -> DynamicModule:
            if extras is not None:
                self._extras = extras
            provider = ModuleProviderDict(
                token=MODULE_OPTION_TOKEN,
                factory=factory,
                inject=inject or [],
                use_class=use_class,
                existing=existing,
                value=value,
                imports=imports,
            )
            return self._create_dynamic_module(cls_, imports or [], [provider])

        cls = type(
            "ConfigurableModuleClass",
            (object,),
            {
                self._method_name: classmethod(register),
                f"{self._method_name}_async": classmethod(register_async),
            },
        )
        return cls, MODULE_OPTION_TOKEN
