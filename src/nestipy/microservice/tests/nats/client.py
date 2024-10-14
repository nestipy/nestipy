import asyncio

from nestipy.microservice.client import NatsClientProxy, MicroserviceOption


async def main():
    client = NatsClientProxy(
        MicroserviceOption(url="nats://localhost:4222"),
    )
    await client.send("topic", "request")


if __name__ == "__main__":
    asyncio.run(main())
