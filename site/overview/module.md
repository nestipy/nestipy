A module is a class annotated with a `@Module()` decorator. The `@Module()` decorator provides metadata that **Nestipy** makes use of to organize the application structure.
For **Nestipy**, module works like **NestJs** module . It support **re-exporting** as same as <b>NestJs</b>.
The `@Module()` decorator takes positionals properties that describe the module:

* providers
* controllers
* exports
* imports
* is_global

This is how it look like.
```python
from nestipy.common import Module


@Module(
    providers=[],  # list of providers
    controllers=[],  # list of controllers,
    imports=[],  # list of imported modules
    exports=[],  # list of module or providers exported for module
    is_global=False  # define if module is global or note, 
)
class AppModule:
    ...
```

## Dynamic modules

Following is an example of a dynamic module definition for a `DatabaseModule`:

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
            exports=[]
        )
```

If we want to use params from `@Module()` decorator in dynamic module, we must do like the following example.

```python
from dataclasses import dataclass
from typing import Annotated

from nestipy.dynamic_module import DynamicModule
from nestipy.ioc import Inject
from nestipy.metadata import Reflect, ModuleMetadata

from nestipy.common import Module, ModuleProviderDict, Injectable


@dataclass
class DatabaseOption:
    option: str = ''


DATABASE_OPTION = 'DATABASE_OPTION'


@Injectable()
class DatabaseService:
    option: Annotated[DatabaseOption, Inject(DATABASE_OPTION)]


@Module(
    is_global=True,
    providers=[DatabaseService]
)
class DatabaseModule:
    # this will be an instance of DatabaseOption 

    @classmethod
    def register(cls, option: DatabaseOption) -> DynamicModule:
        return DynamicModule(
            module=cls,
            providers=[ModuleProviderDict(token=DATABASE_OPTION, value=option)] + Reflect.get_metadata(
                cls,
                ModuleMetadata.Providers,
                []
            ),
            controllers=[] + Reflect.get_metadata(cls, ModuleMetadata.Controllers, []),
            imports=[] + Reflect.get_metadata(cls, ModuleMetadata.Imports, []),
            exports=[] + Reflect.get_metadata(cls, ModuleMetadata.Exports, []),
            is_global=Reflect.get_metadata(cls, ModuleMetadata.Global, False)
        )
```

To facilitate creating of Dynamic module, Nestipy provide `ConfigurableModuleBuilder` class
rom `nestipy.dynamic_module`.

This is an example.

```python
from dataclasses import dataclass
from nestipy.common import Module
from typing import Annotated
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Inject


@dataclass
class DatabaseOption:
    option: str = ''


ConfigurableModuleClass, DATABASE_MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[DatabaseOption]().set_method(
    'for_root').build()


@Module()
class DatabaseModule(ConfigurableModuleClass):
    option: Annotated[DatabaseOption, Inject(DATABASE_MODULE_OPTION_TOKEN)]

```

For this, we will call `DatabaseModule.for_root(option)` or `DatabaseModule.for_root_async(option_async)` to register
Module. The default method to call is `register` and `register_async` if it's not defined.

For a lifecycle hooks, we need to extends `NestipyModule`.

```python
from dataclasses import dataclass
from typing import Annotated
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.dynamic_module import NestipyModule
from nestipy.ioc import Inject


@dataclass
class DatabaseOption:
    option: str = ''


ConfigurableModuleClass, DATABASE_MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[DatabaseOption]().set_method(
    'for_root').build()


class DatabaseModule(ConfigurableModuleClass, NestipyModule):
    option: Annotated[DatabaseOption, Inject(DATABASE_MODULE_OPTION_TOKEN)]

    async def on_startup(self):
        pass

    async def on_shutdown(self):
        pass


```

<br/>
<br/>
