from nestipy.common.decorator import Injectable


@Injectable()
class GuardService:

    async def list(self):
        return "test"

    async def delete(self, id: int):
        return "test"
