import os.path

import uvicorn

from app_module import AppModule
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

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
