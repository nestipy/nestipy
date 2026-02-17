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

## Runtime Flags (Env)

Nestipy also supports lightweight runtime flags without the config module:

- `NESTIPY_DEBUG=1` to enable debug behavior (0/false disables).
- `NESTIPY_SECURITY_HEADERS=0` to disable default security headers.
- `NESTIPY_HEALTH=0` to disable built-in `/healthz` and `/readyz`.
- `NESTIPY_CORS_ALLOW_ALL=1` to allow any origin.
- `NESTIPY_CORS_ORIGINS=http://localhost:5173,https://example.com`
- `NESTIPY_CORS_ALLOW_METHODS=GET,POST,PUT,PATCH,DELETE,OPTIONS`
- `NESTIPY_CORS_ALLOW_HEADERS=Content-Type,Authorization,X-Request-Id`
- `NESTIPY_CORS_EXPOSE_HEADERS=X-Request-Id`
- `NESTIPY_CORS_ALLOW_CREDENTIALS=1`
- `NESTIPY_CORS_MAX_AGE=600`
- `NESTIPY_CORS_ORIGIN_REGEX=^https?://.*\.example\.com$`

For actions security defaults, see [Actions (RPC)](/web/actions).
