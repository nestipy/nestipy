import asyncio

from nestipy.microservice.client import MqttClientProxy, MicroserviceOption
from nestipy.microservice.client.option import MqttClientOption
from nestipy.microservice.server.base import MicroServiceServer


async def main():
    client = MqttClientProxy(
        MicroserviceOption(option=MqttClientOption(hostname="localhost", port=1883)),
    )
    server = MicroServiceServer(pub_sub=client)
    print("Running server ...")
    await server.listen()


if __name__ == "__main__":
    asyncio.run(main())
