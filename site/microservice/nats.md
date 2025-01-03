NATS is an efficient, secure, open-source messaging system designed for cloud-native applications, IoT messaging, and microservices. Written in Go, NATS offers client libraries for many programming languages. It supports both At Most Once and At Least Once delivery and is versatile enough to run on large servers, cloud instances, edge gateways, and IoT devices.
## Installation

```bash
pip install nats-py
```

## Overview#
To use the `NATS` transporter, pass the following options object to the `create_microservice`() method:

```python


from app_module import AppModule

from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, NatsClientOption

app = NestipyFactory.create_microservice(
    AppModule, [
        MicroserviceOption(
            transport=Transport.NATS,
            option=NatsClientOption()
        )
    ]
)
```

##Client

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig, NatsClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register([
            ClientsConfig(
                name="MATH_SERVICE",
                option=MicroserviceOption(
                    transport=Transport.NATS,
                    option=NatsClientOption()
                )
            )
        ]),
    ]
    ...
)
class AppModule:
    ...
```
