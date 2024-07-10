import asyncio

from nestipy.microservice.client import NatsClientProxy
from nestipy.microservice.client.option import MicroserviceOption
from nestipy.microservice.serilaizer import JSONSerializer


async def main():
    client = NatsClientProxy(
        MicroserviceOption(
            url="nats://localhost:4222"
        ),
        serializer=JSONSerializer()
    )
    await client.send("topic", "request")


if __name__ == "__main__":
    asyncio.run(main())
