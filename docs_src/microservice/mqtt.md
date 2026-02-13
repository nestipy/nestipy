MQTT is a lightweight pub/sub protocol, commonly used for IoT and mobile messaging. It is efficient in low-bandwidth or high-latency environments.

## Installation

```bash
pip install aiomqtt
```

## Server Setup

```python
from app_module import AppModule
from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, MqttClientOption

app = NestipyFactory.create_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.MQTT,
            option=MqttClientOption(hostname="localhost", port=1883),
        )
    ],
)
```

## Client Setup

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig
from nestipy.microservice import MqttClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register(
            [
                ClientsConfig(
                    name="MATH_SERVICE",
                    option=MicroserviceOption(
                        transport=Transport.MQTT,
                        option=MqttClientOption(hostname="localhost", port=1883),
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

Common MQTT options:

- `hostname`
- `port`
- `username` and `password`
- `keepalive`
- `transport`
- `tls_context`

Use `MqttClientOption` for full configuration.
