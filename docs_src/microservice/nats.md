NATS is a lightweight, high-performance messaging system well-suited for microservices and event-driven systems.

## Installation

```bash
pip install nats-py
```

## Server Setup

```python
from app_module import AppModule
from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, NatsClientOption

app = NestipyFactory.create_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.NATS,
            option=NatsClientOption(),
        )
    ],
)
```

## Client Setup

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig
from nestipy.microservice import NatsClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register(
            [
                ClientsConfig(
                    name="MATH_SERVICE",
                    option=MicroserviceOption(
                        transport=Transport.NATS,
                        option=NatsClientOption(),
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

Common NATS options:

- `servers`
- `name`
- `user` and `password`
- `token`
- `allow_reconnect`
- `max_reconnect_attempts`

Use `NatsClientOption` for full configuration.
