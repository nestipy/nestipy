import asyncio

from nestipy.microservice.client import MqttClientProxy, MicroserviceOption
from nestipy.microservice.client.option import MicroserviceClientOption
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = MqttClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(host="localhost", port=1883)
        ),
    )
    server = MicroServiceServer(pubsub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
