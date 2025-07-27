import asyncio

from nestipy.microservice.client import RedisClientProxy, MicroserviceOption
from nestipy.microservice.client.option import RedisClientOption, Transport


async def main():
    client = RedisClientProxy(
        MicroserviceOption(
            transport=Transport.REDIS,
            option=RedisClientOption(host="localhost", port=6379),
        ),
    )
    await client.send("test", "request")


if __name__ == "__main__":
    asyncio.run(main())
