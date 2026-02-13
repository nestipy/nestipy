The Redis transporter uses Redis Pub/Sub for message delivery. It is a good fit when you already run Redis and want simple eventing or request-response.

## Installation

```bash
pip install redis
```

## Server Setup

```python
from app_module import AppModule
from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, RedisClientOption

app = NestipyFactory.create_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.REDIS,
            option=RedisClientOption(host="localhost", port=6379),
        )
    ],
)
```

## Client Setup

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig
from nestipy.microservice import RedisClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register(
            [
                ClientsConfig(
                    name="MATH_SERVICE",
                    option=MicroserviceOption(
                        transport=Transport.REDIS,
                        option=RedisClientOption(host="localhost", port=6379),
                    ),
                )
            ]
        )
    ]
)
class AppModule:
    pass
```

## Option Highlights

These are the most common Redis options:

- `host`
- `port`
- `db`
- `password`
- `ssl`
- `socket_timeout`

Use `RedisClientOption` for full configuration.
