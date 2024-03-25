import os.path
from typing import Any

import uvicorn

from app_module import AppModule
from nestipy.common.exception.filter import ExceptionFilter, Catch
from nestipy.common.exception.http import HttpException
from nestipy.core.context.argument_host import ArgumentHost
from nestipy.core.nestipy_factory import NestipyFactory
from nestipy.openapi.document_builder import DocumentBuilder
from nestipy.openapi.swagger_module import SwaggerModule

app = NestipyFactory.create(AppModule)
app.enable_cors()
config = DocumentBuilder().set_title('Example API') \
    .set_description('The API description').set_version('1.0').add_bearer_auth().add_basic_auth().build()
SwaggerModule.setup('api', app, config)

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

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
