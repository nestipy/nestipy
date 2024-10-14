import asyncio

from nestipy.microservice.client import NatsClientProxy, MicroserviceOption
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = NatsClientProxy(
        MicroserviceOption(url="nats://localhost:4222"),
    )
    server = MicroServiceServer(pubsub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
