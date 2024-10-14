import asyncio

from nestipy.microservice.client import RabbitMQClientProxy, MicroserviceOption
from nestipy.microservice.client.option import MicroserviceClientOption


async def main():
    client = RabbitMQClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(host="localhost", port=5672)
        ),
    )
    await client.send("topic", "request")


if __name__ == "__main__":
    asyncio.run(main())
