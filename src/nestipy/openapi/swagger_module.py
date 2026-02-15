import dataclasses
import os.path
from typing import TYPE_CHECKING, cast, Optional

import aiofiles
import ujson

from nestipy.common.http_ import Request, Response
from nestipy.metadata import Reflect
from .constant import OPENAPI_HANDLER_METADATA
from .openapi_docs.common import Serializer
from .openapi_docs.v3 import OpenAPI

if TYPE_CHECKING:
    from ..core.nestipy_application import NestipyApplication


@dataclasses.dataclass
class _Document:
    json: str
    yml: str
    obj: dict


class SwaggerModule:
    @classmethod
    def remove_null(cls, json_data):
        if isinstance(json_data, dict):
            return {
                key: cls.remove_null(value)
                for key, value in json_data.items()
                if value is not None
            }
        elif isinstance(json_data, list):
            return [cls.remove_null(item) for item in json_data if item is not None]
        else:
            return json_data

    @classmethod
    def _create_document(cls, app: "NestipyApplication", config: OpenAPI) -> _Document:
        app.build_openapi()
        paths = app.get_openapi_paths()
        config.paths = paths
        schemas_data = app.get_open_api_schemas()
        if schemas_data and "schemas" in schemas_data and config.components:
            existing_schemas = config.components.schemas or {}
            config.components.schemas = {
                **existing_schemas,
                **cast(dict, schemas_data["schemas"]),
            }
        serializer = Serializer()
        json = serializer.to_json(config)
        document_json = ujson.dumps(
            cls.remove_null(ujson.loads(json)), allow_nan=False, indent=4
        )
        document_yml = serializer.to_yaml(config)
        document_obj = serializer.to_obj(config)
        return _Document(document_json, document_yml, document_obj)

    @classmethod
    def setup(cls, path: str, app: "NestipyApplication", config: OpenAPI):
        def register_open_api():
            document_cache: Optional[_Document] = None

            def get_document() -> _Document:
                nonlocal document_cache
                if document_cache is None:
                    document_cache = cls._create_document(app, config)
                return document_cache

            api_path = f"/{path.strip('/')}"

            async def openapi_json_handler(_req: Request, res: Response, _next_fn):
                document = get_document()
                return (
                    await res.status(200)
                    .header("Content-Type", "application/json")
                    .send(document.json)
                )

            async def openapi_yml_handler(_req: Request, res: Response, _next_fn):
                document = get_document()
                return (
                    await res.status(200)
                    .header("Content-Type", "text/yml")
                    .send(document.yml)
                )

            async def openapi_swagger_handler(_req: Request, res: Response, _next_fn):
                file = await aiofiles.open(
                    os.path.join(os.path.dirname(__file__), "swagger.html"), "r"
                )
                html = await file.read()
                devtools_static = app.get_devtools_static_path()
                html = html.replace("/_devtools/static", devtools_static)
                response = await res.status(200).html(html)
                await file.close()
                return response

            http_adapter = app.get_adapter()
            raw_meta = {"raw": True}
            http_adapter.get("/openapi.json", openapi_json_handler, raw_meta)
            http_adapter.get("/openapi.yml", openapi_yml_handler, raw_meta)
            http_adapter.get(api_path, openapi_swagger_handler, raw_meta)

        Reflect.set_metadata(app, OPENAPI_HANDLER_METADATA, register_open_api)
