import random

import uvicorn
from nestipy.core import NestipyFactory
from nestipy.microservice import MicroserviceOption, Transport, MicroserviceClientOption

from app_module import AppModule

app = NestipyFactory.create_microservice(
    AppModule,
    [
        MicroserviceOption(
            transport=Transport.REDIS,
            option=MicroserviceClientOption(host="localhost", port=6379),
        )
    ],
)
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=random.randint(5000, 7000),
        reload=True,
        log_level="critical",
    )
