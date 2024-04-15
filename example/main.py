import os.path
from typing import Any

import socketio
import uvicorn

from app_module import AppModule
from nestipy.common.exception.filter import ExceptionFilter, Catch
from nestipy.common.exception.http import HttpException
from nestipy.core.context.argument_host import ArgumentHost
from nestipy.core.nestipy_factory import NestipyFactory
from nestipy.core.platform import NestipyFastApiApplication
from nestipy.openapi import SwaggerModule, DocumentBuilder
from nestipy.websocket import SocketIoAdapter

# default use blacksheep
app = NestipyFactory[NestipyFastApiApplication].create(AppModule)
# enable cors
app.enable_cors()
# setup swagger
document = DocumentBuilder().set_title('Example API') \
    .set_description('The API description').set_version('1.0').add_bearer_auth().add_basic_auth().build()
SwaggerModule.setup('api', app, document)

# serve static file
app.use_static_assets(os.path.join(os.path.dirname(__file__), 'public'))

# Template rendering
app.set_base_view_dir(os.path.join(os.path.dirname(__file__), 'views'))
app.set_view_engine('minimal-jinja')


@Catch()
class TestGlobalFilter(ExceptionFilter):

    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        return await host.get_response().status(exception.status_code).json({
            'status': exception.status_code,
            'error': exception.message,
            'details': exception.details
        })


app.use_global_filters(TestGlobalFilter)

# socket io
sio = socketio.AsyncServer(async_mode='asgi')
app.use_io_adapter(SocketIoAdapter(sio))


@app.on_startup
async def startup():
    print('Starting up ...')


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
