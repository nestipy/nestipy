import asyncio

from nestipy.microservice.client import MqttClientProxy, MicroserviceOption
from nestipy.microservice.client.option import MicroserviceClientOption


async def main():
    client = MqttClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(host="localhost", port=1883)
        ),
    )
    await client.send("topic", "request")


if __name__ == "__main__":
    asyncio.run(main())
