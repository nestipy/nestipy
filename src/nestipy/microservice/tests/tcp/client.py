import asyncio

from nestipy.microservice import Transport
from nestipy.microservice.client import TCPClientProxy, MicroserviceOption


async def main():
    client = TCPClientProxy(
        option=MicroserviceOption(transport=Transport.TCP),
    )
    response = await client.send("test", "request")
    print("Response from server:", response.data)


if __name__ == "__main__":
    asyncio.run(main())
