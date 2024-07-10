import asyncio

from nestipy.microservice.client import NatsClientProxy
from nestipy.microservice.client.option import MicroserviceOption
from nestipy.microservice.serilaizer import JSONSerializer
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    serializer = JSONSerializer()
    client = NatsClientProxy(
        MicroserviceOption(
            url="nats://localhost:4222"
        ),
        serializer
    )
    server = MicroServiceServer(pubsub=client, serializer=serializer)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
