import asyncio

from nestipy.microservice.client import MqttClientProxy
from nestipy.microservice.client.option import MicroserviceOption, MicroserviceClientOption
from nestipy.microservice.serilaizer import JSONSerializer
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    serializer = JSONSerializer()
    client = MqttClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(
                host='localhost',
                port=1883
            )
        ),
        serializer
    )
    server = MicroServiceServer(pubsub=client, serializer=serializer)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
