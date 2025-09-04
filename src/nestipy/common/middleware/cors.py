from typing import Type
from nestipy.common.decorator import Injectable
from nestipy.types_ import NextFn
from nestipy.common.middleware.interface import NestipyMiddleware
from nestipy.common.http_ import Request, Response


def cors(allowed_origins: list[str] = ["*"]) -> Type:
    @Injectable()
    class CorsMiddleware(NestipyMiddleware):
        async def use(self, req: Request, res: Response, next_fn: NextFn):
            origin = req.headers.get("origin")
            if origin in allowed_origins:
                res.header("access-control-allow-origin", origin)
                res.header("access-control-allow-credentials", "true")
            else:
                res.header("access-control-allow-origin", "*")

            res.header("access-control-allow-headers", "content-type, authorization")
            if req.method.upper() == "OPTIONS":
                return await res.status(204).send("")

            # Continue normal request
            return await next_fn()

    return CorsMiddleware
