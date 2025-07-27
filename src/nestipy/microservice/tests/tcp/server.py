import asyncio

from nestipy.microservice.client import TCPClientProxy, MicroserviceOption
from nestipy.microservice.client.option import TCPClientOption
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = TCPClientProxy(
        MicroserviceOption(option=TCPClientOption()),
    )
    server = MicroServiceServer(pub_sub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
