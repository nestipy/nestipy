import random

import uvicorn

from app_module import AppModule
from nestipy.common import session
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
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=random.randint(5000, 7000),
        reload=True,
        # log_level="critical",
    )
