MQTT (Message Queuing Telemetry Transport) is an open-source messaging protocol known for its efficiency and low latency. It uses a publish/subscribe model, making it a scalable and cost-effective solution for connecting devices. An MQTT communication system includes a publishing server, a broker, and multiple clients. This protocol is ideal for devices with limited resources and networks with low bandwidth, high latency, or instability.
## Installation

```bash
pip install aiomqtt
```

## Overview#
To use the Mqtt transporter, pass the following options object to the `create_microservice`() method:

```python


from app_module import AppModule

from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, MqttClientOption

app = NestipyFactory.create_microservice(
    AppModule, [
        MicroserviceOption(
            transport=Transport.MQTT,
            option=MqttClientOption(
                hostname="localhost",
                port=1883
            )
        )
    ]
)
```

##Client

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig, MqttClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register([
            ClientsConfig(
                name="MATH_SERVICE",
                option=MicroserviceOption(
                    transport=Transport.MQTT,
                    option=MqttClientOption(
                        hostname="localhost",
                        port=1883
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

