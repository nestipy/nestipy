gRPC (gRPC Remote Procedure Call) is an open-source framework developed by Google for high-performance, language-agnostic remote procedure calls (RPC). It enables communication between distributed systems and microservices by allowing clients to directly invoke methods on a server as if it were a local object.
## Installation

```bash
pip install grpcio grpcio-tools
```

## Overview#
To use the Mqtt transporter, pass the following options object to the `create_microservice`() method:

```python


from app_module import AppModule

from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, GrpcClientOption

app = NestipyFactory.create_microservice(
    AppModule, [
        MicroserviceOption(
            transport=Transport.GRPC,
            option=GrpcClientOption(
                host="localhost",
                port=50051
            )
        )
    ]
)
```

##Client

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig, GrpcClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register([
            ClientsConfig(
                name="MATH_SERVICE",
                option=MicroserviceOption(
                    transport=Transport.GRPC,
                    option=GrpcClientOption(
                        host="localhost",
                        port=GRPC
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

