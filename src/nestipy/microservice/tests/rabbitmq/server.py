import asyncio

from nestipy.microservice.client import RabbitMQClientProxy, MicroserviceOption
from nestipy.microservice.client.option import MicroserviceClientOption
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = RabbitMQClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(host="localhost", port=5672)
        ),
    )
    server = MicroServiceServer(pubsub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
