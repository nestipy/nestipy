Let's start directly with and example. We are going to create `ConfigModule` like `ConfigModule` from NestJs.

```python
from dataclasses import dataclass
from os import path, getcwd
from typing import Union, Annotated

from dotenv import dotenv_values
from nestipy.common import Module, Injectable
from nestipy.dynamic_module import ConfigurableModuleBuilder
from nestipy.ioc import Inject


@dataclass
class ConfigOption:
    dir: str = getcwd()


ConfigurableModuleClass, MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[ConfigOption]().build()


@Injectable()
class ConfigService:
    _config: Annotated[ConfigOption, Inject(MODULE_OPTION_TOKEN)]
    _envs: dict = {}

    def __init__(self):
        file = path.join(self._config.dir, '.env')
        _envs: dict = dotenv_values(file)

    def get(self, key: str) -> Union[str, None]:
        if key in self._envs.keys():
            return self._envs.get(key)
        return None


@Module(
    providers=[ConfigService],
    exports=[ConfigService]
)
class ConfigModule(ConfigurableModuleClass):
    pass
```

So, let's view how to use it.

```python
from nestipy.common import Module


@Module(
    imports=[
        ConfigModule.register()  # we can define ConfigOption in register
        # ConfigModule.register(options=ConfigOption(dir=getcwd()))
    ],
    ...
)
class AppModule:
    pass
```

Now, we can use `ConfigModule` in controller or a service provider by injecting it.

```python
from nestipy.ioc import Inject
from typing import Annotated
from nestipy.common import Controller


@Controller('cats')
class CatsController:
    config_service: Annotated[ConfigService, Inject()]
```

Inside service,

```python
from typing import Annotated
from nestipy.common import Injectable
from nestipy.ioc import Inject


@Injectable()
class CatsService:
    config_service: Annotated[ConfigService, Inject()]
```

Using it inside async factory.

```python
from dataclasses import dataclass
from typing import Annotated

from nestipy.dynamic_module import ConfigurableModuleBuilder, NestipyModule
from nestipy.ioc import Inject

from nestipy.common import ConfigModule, ConfigService
from nestipy.common import Module


@dataclass
class DatabaseConfigOption:
    host: str
    password: str
    user: str
    port: int = 3306


ConfigurableModuleClass, MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[DatabaseConfigOption]().set_method(
    'for_root').build()


@Module()
class DatabaseModule(ConfigurableModuleClass, NestipyModule):
    option: Annotated[DatabaseConfigOption, Inject(MODULE_OPTION_TOKEN)]

    def on_startup(self):
        # start connection to database by using option
        pass

    def on_shutdown(self):
        # stop connection to database
        pass


async def database_config_factory(config: Annotated[ConfigService, Inject()]) -> DatabaseConfigOption:
    return DatabaseConfigOption(
        host=config.get('DB_HOST'),
        port=int(config.get('DB_PORT')),
        password=config.get('DB_PASSWORD'),
        user=config.get('DB_USER')
    )


@Module(
    imports=[
        ConfigModule.register(),
        DatabaseModule.for_root_async(
            factory=database_config_factory,
            inject=[ConfigService]
        )
    ]
)
class AppModule:
    pass
```

Note: We can inject service directly inside `Module` if we want to use `DatabaseService` with lifecycle hook
inside `DatabaseModule

Take a look **[here](https://github.com/nestipy/sample/tree/main/sample-app-dynamic-module)** for an example.
