from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
    Literal,
)

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


class ConfigurableModuleBase(Protocol, Generic[T]):
    @classmethod
    def register(
        cls, options: Optional[T], extras: Optional[Dict[str, Any]] = None
    ) -> DynamicModule: ...

    @classmethod
    def register_async(
        cls,
        value: Optional[T] = None,
        factory: Optional[Callable[..., Union[Awaitable[Any], Any]]] = None,
        existing: Optional[Union[Type, str]] = None,
        use_class: Optional[Type] = None,
        inject: Optional[list] = None,
        imports: Optional[list] = None,
        extras: Optional[dict] = None,
    ) -> DynamicModule: ...


class ConfigurableModuleWithForRoot(ConfigurableModuleBase[T], Protocol):
    @classmethod
    def for_root(
        cls, options: Optional[T], extras: Optional[Dict[str, Any]] = None
    ) -> DynamicModule: ...

    @classmethod
    def for_root_async(
        cls,
        value: Optional[T] = None,
        factory: Optional[Callable[..., Union[Awaitable[Any], Any]]] = None,
        existing: Optional[Union[Type, str]] = None,
        use_class: Optional[Type] = None,
        inject: Optional[list] = None,
        imports: Optional[list] = None,
        extras: Optional[dict] = None,
    ) -> DynamicModule: ...


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

    @overload
    def set_method(
        self, name: Literal["for_root"]
    ) -> "ConfigurableModuleBuilderForRoot[T]": ...

    @overload
    def set_method(self, name: str) -> "ConfigurableModuleBuilder[T]": ...

    def set_method(self, name: str):
        self._method_name = name
        if name == "for_root":
            return cast(ConfigurableModuleBuilderForRoot[T], self)
        return self

    def _extra_return(self, dynamic_module: DynamicModule) -> DynamicModule:
        if self._extras is not None and self._extras_process_callback is not None:
            self._extras_process_callback(dynamic_module, self._extras)
        return dynamic_module

    def create_dynamic_module(
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

    @overload
    def build(
        self: "ConfigurableModuleBuilderForRoot[T]",
    ) -> tuple[type[ConfigurableModuleWithForRoot[T]], str]: ...

    @overload
    def build(self) -> tuple[type[ConfigurableModuleBase[T]], str]: ...

    def build(self) -> tuple[Type, str]:
        module_option_token = f"{uuid.uuid4().hex}_TOKEN"

        def register(
            cls_: Any, options: Optional[T], extras: Optional[dict] = None
        ) -> DynamicModule:
            if extras is not None:
                self._extras = extras
            provider = ModuleProviderDict(token=module_option_token, value=options)
            return self.create_dynamic_module(cls_, [], [provider])

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
                token=module_option_token,
                factory=factory,
                inject=inject or [],
                use_class=use_class,
                existing=existing,
                value=value,
                imports=imports,
            )
            return self.create_dynamic_module(cls_, imports or [], [provider])

        annotations = {
            "register": Callable[
                [Any, Optional[T], Optional[Dict[str, Any]]], DynamicModule
            ],
            "register_async": Callable[
                [
                    Any,
                    Optional[T],
                    Optional[Callable[..., Union[Awaitable[Any], Any]]],
                    Optional[Union[Type, str]],
                    Optional[Type],
                    Optional[List[Any]],
                    Optional[List[Any]],
                    Optional[Dict[str, Any]],
                ],
                DynamicModule,
            ],
        }
        attrs: dict[str, Any] = {
            "__annotations__": annotations,
            "register": classmethod(register),
            "register_async": classmethod(register_async),
        }
        if self._method_name != "register":
            annotations[self._method_name] = annotations["register"]
            annotations[f"{self._method_name}_async"] = annotations["register_async"]
            attrs[self._method_name] = classmethod(register)
            attrs[f"{self._method_name}_async"] = classmethod(register_async)

        cls = type("ConfigurableModuleClass", (object,), attrs)
        return cls, module_option_token


class ConfigurableModuleBuilderForRoot(ConfigurableModuleBuilder[T]):
    """Typed builder that advertises for_root helpers for editors."""
