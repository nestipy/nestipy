import asyncio

from nestipy.microservice.client import RedisClientProxy, MicroserviceOption
from nestipy.microservice.client.option import MicroserviceClientOption
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = RedisClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(host="localhost", port=6379)
        ),
    )
    server = MicroServiceServer(pubsub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
