A module is a class annotated with `@Module()`. Modules organize providers, controllers, and imports, and define clear dependency boundaries. Nestipy modules follow the same mental model as NestJS.

## Module Metadata

`@Module()` accepts these fields:

- `providers`: Classes or custom providers that the module creates.
- `controllers`: Controllers owned by this module.
- `imports`: Other modules to pull in.
- `exports`: Providers or modules made available to imports.
- `is_global`: If true, exports are available everywhere without importing.

```python
from nestipy.common import Module


@Module(
    providers=[],
    controllers=[],
    imports=[],
    exports=[],
    is_global=False,
)
class AppModule:
    pass
```

## Import and Export Rules

A provider is visible inside its own module. Other modules can use it only if:

- The provider is exported by its module.
- The module is imported by the consumer.

This makes module boundaries explicit and predictable.

## Global Modules

If a module is marked `is_global=True`, its exports are available everywhere. Use this for cross-cutting concerns like config, logging, or shared clients. Avoid overusing global modules to keep dependencies explicit.

## Dynamic Modules

Dynamic modules let you pass configuration at registration time. This is useful for database modules, clients, and feature toggles.

```python
from nestipy.common import Module
from nestipy.dynamic_module import DynamicModule


@Module()
class DatabaseModule:
    @classmethod
    def register(cls) -> DynamicModule:
        return DynamicModule(
            module=cls,
            providers=[],
            controllers=[],
            imports=[],
            exports=[],
        )
```

If you want to reuse metadata from `@Module()`, merge it into the dynamic module:

```python
from dataclasses import dataclass
from typing import Annotated

from nestipy.dynamic_module import DynamicModule
from nestipy.ioc import Inject
from nestipy.metadata import Reflect, ModuleMetadata
from nestipy.common import Module, ModuleProviderDict, Injectable


@dataclass
class DatabaseOption:
    option: str = ""


DATABASE_OPTION = "DATABASE_OPTION"


@Injectable()
class DatabaseService:
    option: Annotated[DatabaseOption, Inject(DATABASE_OPTION)]


@Module(
    is_global=True,
    providers=[DatabaseService],
)
class DatabaseModule:
    @classmethod
    def register(cls, option: DatabaseOption) -> DynamicModule:
        return DynamicModule(
            module=cls,
            providers=[
                ModuleProviderDict(token=DATABASE_OPTION, value=option),
                *Reflect.get_metadata(cls, ModuleMetadata.Providers, []),
            ],
            controllers=Reflect.get_metadata(cls, ModuleMetadata.Controllers, []),
            imports=Reflect.get_metadata(cls, ModuleMetadata.Imports, []),
            exports=Reflect.get_metadata(cls, ModuleMetadata.Exports, []),
            is_global=Reflect.get_metadata(cls, ModuleMetadata.Global, False),
        )
```

## ConfigurableModuleBuilder

`ConfigurableModuleBuilder` reduces boilerplate by creating `register` and `register_async` for you.

```python
from dataclasses import dataclass
from typing import Annotated

from nestipy.common import Module
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Inject


@dataclass
class DatabaseOption:
    option: str = ""


ConfigurableModuleClass, DATABASE_MODULE_OPTION_TOKEN = (
    ConfigurableModuleBuilder[DatabaseOption]().set_method("for_root").build()
)


@Module()
class DatabaseModule(ConfigurableModuleClass):
    option: Annotated[DatabaseOption, Inject(DATABASE_MODULE_OPTION_TOKEN)]
```

You can then register with `DatabaseModule.for_root(option)` or `DatabaseModule.for_root_async(...)`.

## Module Lifecycle

If you need lifecycle hooks and middleware configuration, extend `NestipyModule` and implement its hooks. See the lifecycle documentation for the full order and available hooks.
