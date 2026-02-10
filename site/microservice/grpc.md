gRPC is a high-performance RPC framework by Google. It enables strongly typed service contracts and efficient binary transport.

## Installation

```bash
pip install grpcio grpcio-tools
```

## Server Setup

```python
from app_module import AppModule
from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, GrpcClientOption

app = NestipyFactory.create_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.GRPC,
            option=GrpcClientOption(host="localhost", port=50051),
        )
    ],
)
```

## Client Setup

```python
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig
from nestipy.microservice import GrpcClientOption, MicroserviceOption, Transport


@Module(
    imports=[
        ClientsModule.register(
            [
                ClientsConfig(
                    name="MATH_SERVICE",
                    option=MicroserviceOption(
                        transport=Transport.GRPC,
                        option=GrpcClientOption(host="localhost", port=50051),
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

Common gRPC options:

- `host`
- `port`
- `verbose`

Use `GrpcClientOption` for full configuration.
