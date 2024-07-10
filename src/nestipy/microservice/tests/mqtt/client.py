import asyncio

from nestipy.microservice.client import MqttClientProxy
from nestipy.microservice.client.option import MicroserviceOption, MicroserviceClientOption
from nestipy.microservice.serilaizer import JSONSerializer


async def main():
    client = MqttClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(
                host='localhost',
                port=1883
            )
        ),
        serializer=JSONSerializer()
    )
    await client.send("topic", "request")


if __name__ == "__main__":
    asyncio.run(main())
