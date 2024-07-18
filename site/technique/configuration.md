Nestipy offers a module comparable to `@nestjs/config`, allowing you to load data from environment variables or a `.env` file, similar to the feature in NestJs.
## Installation
To begin using it, we first install the required dependency.
```bash
pip install nestipy_config
```
To simplify configuration, `nestipy_config` offer two methods to register the `ConfigModule`: `for_root` and `for_root_async`.
Bellow is an example with `for_root` method.

```python
from nestipy_config import ConfigModule, ConfigOption
from nestipy.common import Module

@Module(
    imports=[
         ConfigModule.for_root(ConfigOption(), is_global=True)
    ]
)
class AppModule:
    ...
```

After that, we can inject `ConfigService` in any controller or any provider.

```python
from typing import Annotated
from nestipy.common import Injectable
from nestipy.ioc import Inject
from nestipy_config import ConfigService


@Injectable()
class AppService:
    config_service: Annotated[ConfigService, Inject()]
```