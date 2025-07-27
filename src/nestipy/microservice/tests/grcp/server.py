import asyncio

from nestipy.microservice.client import GrpcClientProxy, MicroserviceOption
from nestipy.microservice.client.option import GrpcClientOption, Transport
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = GrpcClientProxy(
        MicroserviceOption(transport=Transport.GRPC, option=GrpcClientOption()),
    )
    server = MicroServiceServer(pub_sub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
