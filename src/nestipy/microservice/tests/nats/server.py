import asyncio

from nestipy.microservice import NatsClientOption, Transport
from nestipy.microservice.client import NatsClientProxy, MicroserviceOption
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = NatsClientProxy(
        MicroserviceOption(transport=Transport.NATS, option=NatsClientOption()),
    )
    server = MicroServiceServer(pub_sub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
