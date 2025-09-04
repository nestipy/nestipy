from app_controller import AppController
from app_service import AppService
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig, Transport
from nestipy.microservice import MicroserviceOption, GrpcClientOption


@Module(
    imports=[
        ClientsModule.register(
            [
                ClientsConfig(
                    name="TEST_MICROSERVICE",
                    option=MicroserviceOption(
                        transport=Transport.GRPC,
                        option=GrpcClientOption(host="localhost", port=50051),
                    ),
                )
            ]
        )
    ],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule: ...
