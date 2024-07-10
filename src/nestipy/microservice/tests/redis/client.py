import asyncio

from nestipy.microservice.client import RedisClientProxy
from nestipy.microservice.client.option import MicroserviceOption, MicroserviceClientOption
from nestipy.microservice.serilaizer import JSONSerializer


async def main():
    client = RedisClientProxy(
        MicroserviceOption(
            option=MicroserviceClientOption(
                host='localhost',
                port=6379
            )
        ),
        serializer=JSONSerializer()
    )
    await client.send("test", "request")


if __name__ == "__main__":
    asyncio.run(main())
