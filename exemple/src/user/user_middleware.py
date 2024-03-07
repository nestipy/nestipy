from nestipy.common.decorator.middleware import NestipyMiddleware


class UserMiddleware(NestipyMiddleware):

    async def use(self, request, response, next_function):
        print('await UserMiddleware called')
        await next_function()
        print('await after UserMiddleware called')
        return response


async def create_middleware(request, response, next_function):
    print('create_middleware called ')
    return await next_function()
