import os.path
from typing import Any

import socketio
from granian.constants import Interfaces
from app_module import AppModule
from nestipy.common import HttpException, ExceptionFilter, Catch, logger
from nestipy.common import session
from nestipy.core import ArgumentHost, NestipyFactory
from nestipy.core import FastApiApplication, BlackSheepApplication
from nestipy.core.adapter.blacksheep_adapter import BlackSheepAdapter
from nestipy.openapi import SwaggerModule, DocumentBuilder
from nestipy.websocket import WebsocketAdapter
from nestipy.core import NestipyConfig

config = NestipyConfig(
    adapter=BlackSheepAdapter(),
    profile=True,  # boot profiling output
    dependency_graph_debug=True,  # log graph summary to console
    dependency_graph_json_path="deps.json",  # optional: write graph json to file
    router_spec_enabled=True,  # enable /_router/spec
    router_spec_path="/_router/spec",  # optional override
    router_spec_token="secret",  # optional token protection
    # devtools_static_path="/_devtools/<token>/static",  # optional: hide devtools path
)


# default use blacksheep
app = NestipyFactory[BlackSheepApplication].create(AppModule, config=config)
# enable cors
app.enable_cors()
# setup swagger
document = (
    DocumentBuilder()
    .set_title("Nestipy API Documentation")
    .set_description(
        "Nestipy is a Python framework inspired by NestJS and built on top of FastAPI or Blacksheep"
    )
    .set_version("1.0")
    .add_bearer_auth()
    .add_basic_auth()
    .build()
)
SwaggerModule.setup("api", app, document)

# serve static file
app.use_static_assets(os.path.join(os.path.dirname(__file__), "public"))

# Template rendering
app.set_base_view_dir(os.path.join(os.path.dirname(__file__), "views"))
app.set_view_engine("minijinja")


@Catch()
class TestGlobalFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentHost) -> Any:
        return (
            await host.get_response()
            .status(exception.status_code)
            .json(
                {
                    "status": exception.status_code,
                    "error": exception.message,
                    "details": exception.details,
                }
            )
        )


# app.use_global_filters(TestGlobalFilter)

# app.use_global_filters(NotFoundHandler)

# app.use_global_prefix('/v1')
# socket io
sio = socketio.AsyncServer(async_mode="asgi")
# app.use_io_adapter(SocketIoAdapter(sio))
app.use_io_adapter(WebsocketAdapter())

app.use(session())


@app.on_startup
async def startup():
    logger.info("Starting up ...")
    static_path = app.get_devtools_static_path()
    root_path = static_path[: -len("/static")] if static_path.endswith("/static") else static_path
    logger.info("[Devtools] Graph: %s/graph", root_path)
    logger.info("[Devtools] Graph JSON: %s/graph.json", root_path)
    logger.info("[RouterSpec] %s (token required)", config.router_spec_path)

# app.generate_typed_client("clients/api_client.py", class_name="ApiClient")

# # TypeScript client
# app.generate_typescript_client("clients/api_client.ts", class_name="ApiClient")

if __name__ == "__main__":
    app.listen("main:app", address="0.0.0.0", port=8001, interface=Interfaces.ASGI, reload=True)
