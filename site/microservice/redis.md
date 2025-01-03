The Redis transporter uses the publish/subscribe messaging paradigm, leveraging Redis's Pub/Sub feature.
## Installation

```bash
pip install redis
```

## Overview#
To use the Redis transporter, pass the following options object to the `create_microservice`() method:

```python


from app_module import AppModule

from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, RedisClientOption

app = NestipyFactory.create_microservice(
    AppModule, [
        MicroserviceOption(
            transport=Transport.REDIS,
            option=RedisClientOption(
                host="localhost",
                port=6379
            )
        )
    ]
)
```

##Client

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig, RedisClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register([
            ClientsConfig(
                name="MATH_SERVICE",
                option=MicroserviceOption(
                    transport=Transport.REDIS,
                    option=RedisClientOption(
                        host="localhost",
                        port=6379
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

