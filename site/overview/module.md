For **Nestipy**, module works like **NestJs** module . Only module **re-exporting** is not yet supported.

## Dynamic modules

Following is an example of a dynamic module definition for a `DatabaseModule`:

```python
from nestipy.common import Module
from nestipy_dynamic_module import DynamicModule


@Module()
class DatabaseModule:
    @classmethod
    def register(cls) -> DynamicModule:
        return DynamicModule(
            module=cls,
            providers=[],
            controllers=[],
            imports=[],
            exports=[]
        )
```

If we want to use params from `@Module()` decorator in dynamic module, we must do like the following example.

```python
from dataclasses import dataclass

from nestipy_dynamic_module import DynamicModule
from nestipy_ioc import Inject
from nestipy_metadata import Reflect, ModuleMetadata

from nestipy.common import Module, ModuleProviderDict


@dataclass
class DatabaseOption:
    option: str = ''


DATABASE_OPTION = 'DATABASE_OPTION'


@Module(
    is_global=True
)
class DatabaseModule:
    option: Inject[DATABASE_OPTION]  # this will be an instance of DatabaseOption 

    @classmethod
    def register(cls, option: DatabaseOption) -> DynamicModule:
        return DynamicModule(
            module=cls,
            providers=[ModuleProviderDict(token=DATABASE_OPTION, value=option)] + Reflect.get_metadata(cls,
                                                                                                       ModuleMetadata.Providers,
                                                                                                       []),
            controllers=[] + Reflect.get_metadata(cls, ModuleMetadata.Controllers, []),
            imports=[] + Reflect.get_metadata(cls, ModuleMetadata.Imports, []),
            exports=[] + Reflect.get_metadata(cls, ModuleMetadata.Exports, []),
            is_global=Reflect.get_metadata(cls, ModuleMetadata.Global, False)
        )
```

To facilitate creating of Dynamic module, Nestipy provide `ConfigurableModuleBuilder` class.

This is an example.

```python
from dataclasses import dataclass

from nestipy_dynamic_module import ConfigurableModuleBuilder
from nestipy_ioc import Inject


@dataclass
class DatabaseOption:
    option: str = ''


ConfigurableModuleClass, DATABASE_MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[DatabaseOption]().set_method(
    'for_root').build()


class DatabaseModule(ConfigurableModuleClass):
    option: Inject[DATABASE_MODULE_OPTION_TOKEN]

```

For this, we will call `DatabaseModule.for_root(option)` or `DatabaseModule.for_root_async(option_async)` to register
Module. The default method to call is `register` and `register_async` if it's not defined.

For a lifecycle hooks, we need to extends `NestipyModule`.

```python
from dataclasses import dataclass

from nestipy_dynamic_module import ConfigurableModuleBuilder
from nestipy_dynamic_module import NestipyModule
from nestipy_ioc import Inject


@dataclass
class DatabaseOption:
    option: str = ''


ConfigurableModuleClass, DATABASE_MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[DatabaseOption]().set_method(
    'for_root').build()


class DatabaseModule(ConfigurableModuleClass, NestipyModule):
    option: Inject[DATABASE_MODULE_OPTION_TOKEN]

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass


```

<br/>
<br/>