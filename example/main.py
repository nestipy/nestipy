import os.path
from typing import Any

import socketio
import uvicorn

from app_module import AppModule
from nestipy.common import HttpException, ExceptionFilter, Catch, logger
from nestipy.common import session
from nestipy.core import ArgumentHost, NestipyFactory, NestipyFastApiApplication
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
app.set_view_engine('minijinja')


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

app.use(session())


@app.on_startup
async def startup():
    logger.info('Starting up ...')


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
