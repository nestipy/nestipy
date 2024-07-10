import asyncio

from nestipy.microservice.client import RedisClientProxy
from nestipy.microservice.client.option import MicroserviceOption, MicroserviceClientOption
from nestipy.microservice.serilaizer import JSONSerializer
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    serializer = JSONSerializer()
    client = RedisClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(
                host='localhost',
                port=6379
            )
        ),
        serializer
    )
    server = MicroServiceServer(pubsub=client, serializer=serializer)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
