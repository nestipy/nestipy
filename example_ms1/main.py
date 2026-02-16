import random

from granian.constants import Interfaces

from app_module import AppModule

# from nestipy.common import session
from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport

app = NestipyFactory.connect_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.GRPC,
        )
    ],
)

# app.use(session())
app.start_all_microservices()
if __name__ == "__main__":
    app.listen(
        address="0.0.0.0",
        port=random.randint(5000, 7000),
        interface=Interfaces.ASGI,
        reload=True,
    )
