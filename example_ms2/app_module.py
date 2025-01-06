from app_controller import AppController
from app_service import AppService
from nestipy.common import Module
from nestipy.microservice import ClientsModule, ClientsConfig, Transport
from nestipy.microservice import MicroserviceOption, RedisClientOption


@Module(
    imports=[
        ClientsModule.register(
            [
                ClientsConfig(
                    name="TEST_MICROSERVICE",
                    option=MicroserviceOption(
                        transport=Transport.REDIS,
                        option=RedisClientOption(host="localhost", port=6379),
                    ),
                )
            ]
        )
    ],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule: ...
