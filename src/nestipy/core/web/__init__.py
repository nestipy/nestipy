from .devtools_routes import DevtoolsRegistrar, resolve_devtools_static_path
from .web_static import WebStaticHandler

__all__ = [
    "DevtoolsRegistrar",
    "resolve_devtools_static_path",
    "WebStaticHandler",
]
