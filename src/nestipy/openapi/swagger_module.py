import dataclasses

from openapidocs.common import Serializer
from openapidocs.v3 import OpenAPI

from nestipy.common.http_ import Request, Response
from .constant import OPENAPI_HANDLER_METADATA
from ..core.nestipy_application import NestipyApplication


@dataclasses.dataclass
class Document:
    json: str
    yml: str
    obj: dict


class SwaggerModule:

    @classmethod
    def _createDocument(cls, app: NestipyApplication, config: OpenAPI) -> Document:
        paths = app.get_openapi_paths()
        serializer = Serializer()
        config.paths = paths
        document_json = serializer.to_json(config)
        document_yml = serializer.to_yaml(config)
        document_obj = serializer.to_obj(config)
        return Document(document_json, document_yml, document_obj)

    @classmethod
    def setup(cls, path: str, app: NestipyApplication, config: OpenAPI):
        def register_open_api():
            document = cls._createDocument(app, config)
            api_path = f"/{path.strip('/')}"

            async def openapi_json_handler(req: Request, res: Response, next_fn):
                return await res.status(200).header('Content-Type', 'application/json').send(document.json)

            async def openapi_yml_handler(req: Request, res: Response, next_fn):
                return await res.status(200).header('Content-Type', 'application/json').send(document.json)

            async def openapi_swagger_handler(req: Request, res: Response, next_fn):
                return await res.status(200).html(
                    """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta
    name="description"
    content="SwaggerIU"
  />
  <title>SwaggerUI</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.12.0/swagger-ui.min.css"
   integrity="sha512-pV+ep5Xjvc5jwqjAGERsdA00vVaP7eaKd2dYDSEe3sqe3v4ohjue4O51AnLvQGOU2hrlTo7tvLpHXLZfQa9Ubg==" 
   crossorigin="anonymous" referrerpolicy="no-referrer" />
</head>
<body>
  <div id="swagger-ui"></div>
 <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.12.0/swagger-ui-bundle.min.js" 
 integrity="sha512-vGAdoz2QRNOgs8OGP8eKFno/I4jCe+rY6sV8lFaks2UQf7AxPr4e1URRxX/bf8fMUFARO9A+vQ2Jb+XpBiGZyQ==" 
 crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.12.0/swagger-ui-standalone-preset.min.js" 
  integrity="sha512-0nWGki2/3rEDkKQE0AwEJKIHNjyaHhj5x/afJmx9XmhMm3hwibOcRJI+uRlXNbi4ASmgi5lTYxqNY1ldAD5GHg==" 
  crossorigin="anonymous" referrerpolicy="no-referrer"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
      });
    };
  </script>
</body>
</html>"""
                )

            app.get_adapter().get('/openapi.json', openapi_json_handler, {})
            app.get_adapter().get('/openapi.yml', openapi_yml_handler, {})
            app.get_adapter().get(api_path, openapi_swagger_handler, {})

        setattr(app, OPENAPI_HANDLER_METADATA, register_open_api)
