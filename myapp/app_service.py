from nestipy.common import Injectable
from datetime import datetime


@Injectable()
class AppService:
    @classmethod
    async def get(cls):
        return "test - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    async def post(cls, data: dict):
        return "test - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    async def put(cls, id_: int, data: dict):
        return "test - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    async def delete(cls, id_: int):
        return "test - " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")