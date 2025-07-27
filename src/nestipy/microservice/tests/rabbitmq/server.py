import asyncio

from nestipy.microservice.client import RabbitMQClientProxy, MicroserviceOption
from nestipy.microservice.client.option import RabbitMQClientOption
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = RabbitMQClientProxy(
        MicroserviceOption(option=RabbitMQClientOption(host="localhost", port=5672)),
    )
    server = MicroServiceServer(pub_sub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
