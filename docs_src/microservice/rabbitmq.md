RabbitMQ is a robust message broker with multiple protocol options. It is a good choice for durable messaging and complex routing patterns.

## Installation

```bash
pip install aio-pika
```

## Server Setup

```python
from app_module import AppModule
from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, RabbitMQClientOption

app = NestipyFactory.create_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.RABBITMQ,
            option=RabbitMQClientOption(
                host="localhost",
                port=5672,
                login="guest",
                password="guest",
            ),
        )
    ],
)
```

## Client Setup

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig
from nestipy.microservice import RabbitMQClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register(
            [
                ClientsConfig(
                    name="MATH_SERVICE",
                    option=MicroserviceOption(
                        transport=Transport.RABBITMQ,
                        option=RabbitMQClientOption(host="localhost", port=5672),
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

Common RabbitMQ options:

- `host`
- `port`
- `login` and `password`
- `virtualhost`
- `ssl`
- `queue_option`

Use `RabbitMQClientOption` for full configuration.
