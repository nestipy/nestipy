RabbitMQ is a versatile, open-source message broker favored for its support of multiple protocols, scalability in distributed or federated setups, and trusted reliability across global enterprises and startups alike.
## Installation

```bash
pip install aio-pika
```

## Overview#
To use the `RabbitMQ` transporter, pass the following options object to the `create_microservice`() method:

```python


from app_module import AppModule

from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, MicroserviceClientOption

app = NestipyFactory.create_microservice(
    AppModule, [
        MicroserviceOption(
            transport=Transport.RABBITMQ,
            option=MicroserviceClientOption(
                host="localhost",
                port=5672
            )
        )
    ]
)
```

##Client

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig, MicroserviceClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register([
            ClientsConfig(
                name="MATH_SERVICE",
                option=MicroserviceOption(
                    transport=Transport.RABBITMQ,
                    option=MicroserviceClientOption(
                        host="localhost",
                        port=5672
                    )
                )
            )
        ]),
    ]
    ...
)
class AppModule:
    ...
```