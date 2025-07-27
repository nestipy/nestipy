import asyncio

from nestipy.microservice import Transport
from nestipy.microservice.client import GrpcClientProxy, MicroserviceOption


async def main():
    client = GrpcClientProxy(
        option=MicroserviceOption(transport=Transport.GRPC),
    )
    response = await client.send("test", "request")
    print("Response from server:", response.data)


if __name__ == "__main__":
    asyncio.run(main())
