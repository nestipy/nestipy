import uvicorn

from app_module import AppModule
from nestipy.common.middleware import cors
from nestipy.core.nestipy_factory import NestipyFactory
from nestipy.openapi.document_builder import DocumentBuilder
from nestipy.openapi.swagger_module import SwaggerModule

app = NestipyFactory.create(AppModule)
app.use(cors())
config = DocumentBuilder().set_title('Example API') \
    .set_description('The API description').set_version('1.0').add_bearer_auth().add_basic_auth().build()
SwaggerModule.setup('api', app, config)

if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)
