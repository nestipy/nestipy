Let's start directly with and example. We are going to create `ConfigModule` like `ConfigModule` from NestJs.

```python
from dataclasses import dataclass
from os import path, getcwd
from typing import Union

from dotenv import dotenv_values

from nestipy.common import Module, ProviderToken, Injectable
from nestipy.common.dynamic_module import ConfigurableModuleBuilder
from nestipy.types_ import Inject


@dataclass
class ConfigOption:
    dir: str = getcwd()


ConfigurableModuleClass, MODULE_OPTION_TOKEN = ConfigurableModuleBuilder[ConfigOption]().build()


@Injectable()
class ConfigService:
    _config: Inject[ProviderToken(MODULE_OPTION_TOKEN)]
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

So, let's sho ho to use it.

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
from nestipy.common import Controller
from nestipy.types_ import Inject


@Controller('cats')
class CatsController:
    config_service: Inject[ConfigService]
```

Inside service,

```python
from nestipy.common import Injectable
from nestipy.types_ import Inject


@Injectable()
class CatsService:
    config_service: Inject[ConfigService]
```

Using it inside async factory.

```python
from dataclasses import dataclass

from nestipy.common import Module, ProviderToken
from nestipy.common.dynamic_module import ConfigurableModuleBuilder
from nestipy.common.module import NestipyModule
from nestipy.types_ import Inject


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
    option: Inject[ProviderToken(MODULE_OPTION_TOKEN)]

    def on_startup(self):
        # start connection to database by using option
        pass

    def on_shutdown(self):
        # stop connection to database
        pass


async def database_config_factory(config: ConfigModule) -> DatabaseConfigOption:
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
            factory=database_config_factory
        )
    ]
)
class AppModule:
    pass
```

Note: We can inject service directly inside `Module` if we want to use `DatabaseService` with lifecycle hook
inside `DatabaseModule`