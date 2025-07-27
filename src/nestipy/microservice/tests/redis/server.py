import asyncio

from nestipy.microservice.client import RedisClientProxy, MicroserviceOption
from nestipy.microservice.client.option import RedisClientOption, Transport
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = RedisClientProxy(
        MicroserviceOption(
            transport=Transport.REDIS,
            option=RedisClientOption(host="localhost", port=6379),
        ),
    )
    server = MicroServiceServer(pub_sub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
