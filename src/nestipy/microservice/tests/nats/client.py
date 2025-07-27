import asyncio

from nestipy.microservice.client import NatsClientProxy, MicroserviceOption
from nestipy.microservice.client.option import NatsClientOption, Transport


async def main():
    client = NatsClientProxy(
        MicroserviceOption(transport=Transport.NATS, option=NatsClientOption()),
    )
    await client.send("topic", "request")


if __name__ == "__main__":
    asyncio.run(main())
